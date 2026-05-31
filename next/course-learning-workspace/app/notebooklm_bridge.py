from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import importlib.util
import json
import mimetypes
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .store import WorkspaceStore


class NotebookLMBridgeError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def notebooklm_home(store: WorkspaceStore) -> Path:
    configured = os.getenv("NOTEBOOKLM_HOME", "").strip()
    return Path(configured).expanduser() if configured else store.data_dir / "notebooklm"


def notebooklm_storage_path(store: WorkspaceStore) -> Path | None:
    if os.getenv("NOTEBOOKLM_AUTH_JSON", "").strip():
        return None
    return notebooklm_home(store) / "profiles" / "default" / "storage_state.json"


def notebooklm_env(store: WorkspaceStore) -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("NOTEBOOKLM_HOME", str(notebooklm_home(store)))
    return env


def notebooklm_installed() -> bool:
    return importlib.util.find_spec("notebooklm") is not None


def notebooklm_cli() -> str | None:
    return shutil.which("notebooklm")


def auth_check(store: WorkspaceStore, *, test: bool = False) -> dict[str, Any]:
    cli = notebooklm_cli()
    if not cli:
        return {"status": "missing_cli", "ok": False}
    command = [cli, "auth", "check"]
    if test:
        command.append("--test")
    command.append("--json")
    try:
        completed = subprocess.run(
            command,
            cwd=str(Path(__file__).resolve().parents[1]),
            env=notebooklm_env(store),
            capture_output=True,
            text=True,
            timeout=30 if test else 12,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "ok": False}
    output = (completed.stdout or "").strip()
    try:
        parsed = json.loads(output) if output else {}
    except json.JSONDecodeError:
        parsed = {"raw": output[:800]}
    status = str(parsed.get("status") or "").lower()
    return {
        **parsed,
        "status": status or ("ok" if completed.returncode == 0 else "error"),
        "ok": completed.returncode == 0 and (not status or status == "ok"),
        "stderr": (completed.stderr or "").strip()[:800],
    }


def status_payload(store: WorkspaceStore) -> dict[str, Any]:
    state = store.load()
    active = store.active_course(state)
    installed = notebooklm_installed()
    cli = notebooklm_cli()
    auth = auth_check(store, test=False) if cli else {"status": "missing_cli", "ok": False}
    notebook = (active or {}).get("notebooklm") or {}
    return {
        "status": "ok",
        "installed": installed,
        "cli": bool(cli),
        "authenticated": bool(auth.get("ok")),
        "auth": auth,
        "home": str(notebooklm_home(store)),
        "storage_path": str(notebooklm_storage_path(store) or "NOTEBOOKLM_AUTH_JSON"),
        "course_id": (active or {}).get("id"),
        "notebook": notebook,
        "legacy_assistant_disabled": True,
    }


def sync_course(store: WorkspaceStore, *, wait: bool = False) -> dict[str, Any]:
    try:
        return asyncio.run(_sync_course(store, wait=wait))
    except NotebookLMBridgeError:
        raise
    except Exception as exc:
        raise NotebookLMBridgeError(f"NotebookLM sync is not ready: {exc}") from exc


def ask_course(store: WorkspaceStore, question: str) -> dict[str, Any]:
    try:
        return asyncio.run(_ask_course(store, question))
    except NotebookLMBridgeError:
        raise
    except Exception as exc:
        raise NotebookLMBridgeError(f"NotebookLM question is not ready: {exc}") from exc


async def _sync_course(store: WorkspaceStore, *, wait: bool = False) -> dict[str, Any]:
    if not notebooklm_installed():
        raise NotebookLMBridgeError("notebooklm-py is not installed.")
    state = store.load()
    active = store.active_course(state)
    if not active:
        raise NotebookLMBridgeError("Create or select a course before syncing to NotebookLM.")
    os.environ.setdefault("NOTEBOOKLM_HOME", str(notebooklm_home(store)))

    from notebooklm import NotebookLMClient  # type: ignore

    storage_path = notebooklm_storage_path(store)
    async with NotebookLMClient.from_storage(str(storage_path) if storage_path else None) as client:
        notebook_meta = active.setdefault("notebooklm", {})
        notebook_id = str(notebook_meta.get("notebook_id") or "").strip()
        notebook_title = f"CLW - {active.get('name') or 'Course'}"
        if notebook_id:
            try:
                notebook = await client.notebooks.get(notebook_id)
            except Exception:
                notebook = await client.notebooks.create(notebook_title)
                notebook_id = str(notebook.id)
        else:
            notebook = await client.notebooks.create(notebook_title)
            notebook_id = str(notebook.id)

        notebook_meta["notebook_id"] = notebook_id
        notebook_meta["title"] = getattr(notebook, "title", notebook_title) or notebook_title
        source_map = notebook_meta.setdefault("sources", {})
        existing_sources = await client.sources.list(notebook_id)
        existing_by_id = {str(getattr(source, "id", "")): source for source in existing_sources}
        existing_by_title = {normalize_title(getattr(source, "title", "")): source for source in existing_sources}
        uploaded: list[dict[str, str]] = []
        skipped: list[dict[str, str]] = []
        failed: list[dict[str, str]] = []

        for material in active.get("materials", []):
            material_id = str(material.get("id") or "")
            title = str(material.get("title") or material.get("relative_path") or material_id)
            mapped_id = str(source_map.get(material_id) or "")
            if mapped_id and mapped_id in existing_by_id:
                skipped.append({"material_id": material_id, "source_id": mapped_id, "reason": "already_synced"})
                continue
            existing = existing_by_title.get(normalize_title(title))
            if existing:
                source_id = str(getattr(existing, "id", ""))
                source_map[material_id] = source_id
                skipped.append({"material_id": material_id, "source_id": source_id, "reason": "matched_title"})
                continue
            path = store.resolve_material_path(material, active)
            if not path.exists() or not path.is_file():
                failed.append({"material_id": material_id, "title": title, "reason": "file_not_found"})
                continue
            mime_type = mimetypes.guess_type(path.name)[0]
            try:
                source = await client.sources.add_file(
                    notebook_id,
                    str(path),
                    mime_type=mime_type,
                    title=title,
                    wait=wait,
                    wait_timeout=180.0,
                )
            except Exception as exc:
                failed.append({"material_id": material_id, "title": title, "reason": str(exc)[:360]})
                continue
            source_id = str(getattr(source, "id", ""))
            source_map[material_id] = source_id
            uploaded.append({"material_id": material_id, "source_id": source_id, "title": title})

        notebook_meta["source_count"] = len(source_map)
        notebook_meta["synced_at"] = utc_now()
        notebook_meta["last_error"] = ""
        store.save(state)
        return {
            "status": "ok",
            "notebook": notebook_meta,
            "uploaded": uploaded,
            "skipped": skipped,
            "failed": failed,
        }


async def _ask_course(store: WorkspaceStore, question: str) -> dict[str, Any]:
    if not notebooklm_installed():
        raise NotebookLMBridgeError("notebooklm-py is not installed.")
    state = store.load()
    active = store.active_course(state)
    notebook_meta = (active or {}).get("notebooklm") or {}
    notebook_id = str(notebook_meta.get("notebook_id") or "").strip()
    if not active or not notebook_id:
        raise NotebookLMBridgeError("Sync the current course to NotebookLM before asking.")
    clean_question = question.strip()
    if not clean_question:
        raise NotebookLMBridgeError("Question cannot be empty.")
    os.environ.setdefault("NOTEBOOKLM_HOME", str(notebooklm_home(store)))

    from notebooklm import NotebookLMClient  # type: ignore

    source_ids = [str(item) for item in (notebook_meta.get("sources") or {}).values() if str(item).strip()]
    storage_path = notebooklm_storage_path(store)
    async with NotebookLMClient.from_storage(str(storage_path) if storage_path else None) as client:
        result = await client.chat.ask(notebook_id, clean_question, source_ids=source_ids or None)
    references = [_public_object(ref) for ref in getattr(result, "references", [])]
    return {
        "status": "ok",
        "answer": str(getattr(result, "answer", "") or ""),
        "conversation_id": getattr(result, "conversation_id", None),
        "references": references,
        "notebook": notebook_meta,
    }


def normalize_title(value: str) -> str:
    return " ".join(str(value or "").casefold().split())


def _public_object(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if hasattr(value, "to_dict"):
        try:
            return value.to_dict()
        except Exception:
            pass
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_public_object(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _public_object(item) for key, item in value.items()}
    return str(value)
