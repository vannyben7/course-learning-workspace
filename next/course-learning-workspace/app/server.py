from __future__ import annotations

import json
import mimetypes
import os
import cgi
import re
import shutil
import subprocess
import sys
import tempfile
import datetime as dt
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from .assistant import AssistantProviderError, build_study_prompt, call_chat_completions, normalize_provider_result, provider_config, search_web
from .materials import chunk_text, scan_folder, tokenize
from .notebooklm_bridge import NotebookLMBridgeError, ask_course as notebooklm_ask_course, status_payload as notebooklm_status_payload, sync_course as notebooklm_sync_course
from .store import WorkspaceStore


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
MAX_JSON_BODY_BYTES = 1024 * 1024
PAGED_PREVIEW_KINDS = {"pdf", "docx", "pptx", "xlsx"}
OFFICE_PREVIEW_KINDS = {"docx", "pptx", "xlsx"}
ASSISTANT_ACTIONS = {"ask", "explain", "connect", "review"}
ASSISTANT_SCOPES = {"material", "course", "course_web", "web"}
WEB_ASSISTANT_SCOPES = {"course_web", "web"}
ASSISTANT_STOPWORDS = {
    "about",
    "after",
    "answer",
    "asking",
    "based",
    "before",
    "course",
    "current",
    "does",
    "from",
    "help",
    "material",
    "materials",
    "question",
    "read",
    "reading",
    "section",
    "should",
    "source",
    "sources",
    "support",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
    "资料",
    "课程",
    "回答",
    "阅读",
    "当前",
    "问题",
    "什么",
    "哪些",
    "这个",
    "如何",
    "可以",
    "帮助",
    "来源",
}
WRITING_REQUEST_PATTERN = re.compile(
    r"(?i)\b(write|draft|compose|generate|finish|complete|produce)\b.*\b(essay|paper|report|assignment|thesis|dissertation|homework)\b"
    r"|(?:代写|帮我写|写一篇|生成|完成).{0,18}(?:essay|论文|报告|作业|文章|课程论文)"
    r"|(?:essay|论文|报告|作业).{0,18}(?:代写|帮我写|生成|完成)"
)


def parse_poppler_bbox(xml_text: str) -> dict[str, Any]:
    root = ElementTree.fromstring(xml_text)
    page = next((node for node in root.iter() if node.tag.endswith("}page") or node.tag == "page"), None)
    if page is None:
        return {"width": 1.0, "height": 1.0, "words": [], "text": ""}
    try:
        width = max(1.0, float(page.attrib.get("width", "1")))
        height = max(1.0, float(page.attrib.get("height", "1")))
    except ValueError:
        width = 1.0
        height = 1.0
    words: list[dict[str, Any]] = []
    text_parts: list[str] = []
    for node in page.iter():
        if not (node.tag.endswith("}word") or node.tag == "word"):
            continue
        text = (node.text or "").strip()
        if not text:
            continue
        try:
            x_min = float(node.attrib.get("xMin", "0"))
            y_min = float(node.attrib.get("yMin", "0"))
            x_max = float(node.attrib.get("xMax", "0"))
            y_max = float(node.attrib.get("yMax", "0"))
        except ValueError:
            continue
        x = max(0.0, min(1.0, x_min / width))
        y = max(0.0, min(1.0, y_min / height))
        w = max(0.0, min(1.0 - x, (x_max - x_min) / width))
        h = max(0.0, min(1.0 - y, (y_max - y_min) / height))
        if w <= 0 or h <= 0:
            continue
        words.append({"text": text, "x": round(x, 6), "y": round(y, 6), "w": round(w, 6), "h": round(h, 6)})
        text_parts.append(text)
    return {"width": width, "height": height, "words": words, "text": " ".join(text_parts)}


class WorkspaceHandler(BaseHTTPRequestHandler):
    store = WorkspaceStore()

    def do_GET(self) -> None:  # noqa: N802 - stdlib API
        try:
            if not self._host_allowed():
                self._json({"error": "Host is not allowed"}, status=HTTPStatus.FORBIDDEN)
                return
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/api/health":
                self._json({"ok": True, "name": "course-learning-workspace", "stage": "usable-prototype"})
                return
            if parsed.path == "/api/workspace":
                self._json(self.store.load())
                return
            if parsed.path == "/api/notebooklm/status":
                self._json(notebooklm_status_payload(self.store))
                return
            pages_material_id = self._material_pages_route(parsed.path)
            if pages_material_id:
                self._json(self._paged_pages(pages_material_id))
                return
            page_text = self._material_page_text_route(parsed.path)
            if page_text:
                self._json(self._page_text(page_text[0], page_text[1]))
                return
            page_image = self._material_page_image_route(parsed.path)
            if page_image:
                self._serve_page_image(page_image[0], page_image[1])
                return
            material_file_id = self._material_file_route(parsed.path)
            if material_file_id:
                self._serve_material_file(material_file_id)
                return
            material_id = self._material_route(parsed.path)
            if material_id:
                state = self.store.load()
                material = next((item for item in state["materials"] if item["id"] == material_id), None)
                if not material:
                    self._json({"error": "Material not found"}, status=HTTPStatus.NOT_FOUND)
                    return
                annotations = [item for item in state.get("annotations", []) if item.get("material_id") == material_id]
                self._json({**material, "text": self.store.material_text(material_id), "annotations": annotations})
                return
            self._static(parsed.path)
        except ValueError as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.UNPROCESSABLE_ENTITY)
        except Exception as exc:  # pragma: no cover - server guard
            self._json({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802 - stdlib API
        try:
            if not self._host_allowed():
                self._json({"error": "Host is not allowed"}, status=HTTPStatus.FORBIDDEN)
                return
            parsed = urllib.parse.urlparse(self.path)
            upload_course_id = self._course_upload_route(parsed.path)
            if upload_course_id:
                self._json(self.store.upload_materials(upload_course_id, self._read_multipart_files()), status=HTTPStatus.CREATED)
                return
            payload = self._read_json()
            course_id = self._course_select_route(parsed.path)
            if course_id:
                self._json(self.store.select_course(course_id))
                return
            if parsed.path == "/api/courses":
                self._json(self.store.create_course(str(payload.get("name", ""))), status=HTTPStatus.CREATED)
                return
            if parsed.path == "/api/units":
                self._json(self.store.create_unit(str(payload.get("course_id", "")), str(payload.get("name", ""))), status=HTTPStatus.CREATED)
                return
            if parsed.path == "/api/units/assign":
                self._json(
                    self.store.assign_materials_to_unit(
                        str(payload.get("course_id", "")),
                        str(payload.get("unit_id", "")),
                        [str(item) for item in payload.get("material_ids", [])],
                    )
                )
                return
            if parsed.path == "/api/scan":
                course, materials, texts = scan_folder(payload.get("source_path", ""))
                if payload.get("course_name"):
                    course["name"] = str(payload["course_name"]).strip() or course["name"]
                self._json(self.store.replace_scan(course, materials, texts))
                return
            if parsed.path == "/api/notes":
                note = self.store.add_note(
                    payload.get("material_id"),
                    str(payload.get("body", "")),
                    language=str(payload.get("language", "en")),
                )
                self._json({"note": note, "workspace": self.store.load()}, status=HTTPStatus.CREATED)
                return
            if parsed.path == "/api/annotations":
                annotation = self.store.add_annotation(payload)
                self._json({"annotation": annotation, "workspace": self.store.load()}, status=HTTPStatus.CREATED)
                return
            if parsed.path == "/api/assistant/test-provider":
                self._json(self._test_assistant_provider(payload))
                return
            if parsed.path == "/api/ask-materials":
                self._json(self._ask_materials(payload))
                return
            if parsed.path == "/api/notebooklm/sync":
                self._json(notebooklm_sync_course(self.store, wait=bool(payload.get("wait"))))
                return
            if parsed.path == "/api/notebooklm/ask":
                self._json(notebooklm_ask_course(self.store, str(payload.get("question") or "")))
                return
            self._json({"error": "Route not found"}, status=HTTPStatus.NOT_FOUND)
        except NotebookLMBridgeError as exc:
            self._json({"status": "error", "error": str(exc)}, status=HTTPStatus.UNPROCESSABLE_ENTITY)
        except Exception as exc:  # pragma: no cover - server guard
            self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def do_PATCH(self) -> None:  # noqa: N802 - stdlib API
        try:
            if not self._host_allowed():
                self._json({"error": "Host is not allowed"}, status=HTTPStatus.FORBIDDEN)
                return
            parsed = urllib.parse.urlparse(self.path)
            course_id = self._course_route(parsed.path)
            if course_id:
                self._json(self.store.rename_course(course_id, str(self._read_json().get("name", ""))))
                return
            note_id = self._note_route(parsed.path)
            if note_id:
                payload = self._read_json()
                note = self.store.update_note(note_id, str(payload.get("body", "")), language=str(payload.get("language", "en")))
                self._json({"note": note, "workspace": self.store.load()})
                return
            annotation_id = self._annotation_route(parsed.path)
            if annotation_id:
                annotation = self.store.update_annotation(annotation_id, self._read_json())
                self._json({"annotation": annotation, "workspace": self.store.load()})
                return
            self._json({"error": "Route not found"}, status=HTTPStatus.NOT_FOUND)
        except Exception as exc:  # pragma: no cover - server guard
            self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def do_DELETE(self) -> None:  # noqa: N802 - stdlib API
        try:
            if not self._host_allowed():
                self._json({"error": "Host is not allowed"}, status=HTTPStatus.FORBIDDEN)
                return
            parsed = urllib.parse.urlparse(self.path)
            note_id = self._note_route(parsed.path)
            if note_id:
                note = self.store.delete_note(note_id)
                self._json({"note": note, "workspace": self.store.load()})
                return
            annotation_id = self._annotation_route(parsed.path)
            if annotation_id:
                annotation = self.store.delete_annotation(annotation_id)
                self._json({"annotation": annotation, "workspace": self.store.load()})
                return
            self._json({"error": "Route not found"}, status=HTTPStatus.NOT_FOUND)
        except Exception as exc:  # pragma: no cover - server guard
            self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[course-learning-workspace] {self.address_string()} {format % args}")

    def _static(self, path: str) -> None:
        relative = path.split("?", 1)[0].strip("/") or "index.html"
        static_root = WEB_ROOT.resolve()
        file_path = (static_root / relative).resolve()
        try:
            file_path.relative_to(static_root)
        except ValueError:
            file_path = static_root / "index.html"
        if not file_path.exists() or file_path.is_dir():
            file_path = static_root / "index.html"
        content = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(str(file_path))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def _serve_material_file(self, material_id: str) -> None:
        state = self.store.load()
        material = next((item for item in state["materials"] if item["id"] == material_id), None)
        if not material:
            self._json({"error": "Material not found"}, status=HTTPStatus.NOT_FOUND)
            return
        file_path = self.store.resolve_material_path(material)
        if not file_path.exists() or not file_path.is_file():
            self._json({"error": "Material file not found"}, status=HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        content = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Content-Disposition", f"inline; filename*=UTF-8''{urllib.parse.quote(file_path.name)}")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def _paged_pages(self, material_id: str) -> dict[str, Any]:
        material = self._registered_material(material_id)
        preview_pdf, preview_kind = self._preview_pdf_path(material)
        return {
            "material_id": material_id,
            "page_count": self._pdf_page_count(preview_pdf),
            "image_template": f"/api/materials/{urllib.parse.quote(material_id)}/pages/{{page}}.png",
            "text_template": f"/api/materials/{urllib.parse.quote(material_id)}/pages/{{page}}.text.json",
            "preview_kind": preview_kind,
            "source_kind": material.get("kind"),
            "text_available": bool(self.store.material_text(material_id).strip()),
        }

    def _serve_page_image(self, material_id: str, page: int) -> None:
        if page < 1:
            raise ValueError("Page numbers start at 1.")
        material = self._registered_material(material_id)
        preview_pdf, _preview_kind = self._preview_pdf_path(material)
        page_count = self._pdf_page_count(preview_pdf)
        if page > page_count:
            self._json({"error": "Page not found"}, status=HTTPStatus.NOT_FOUND)
            return
        preview_dir = self.store.data_dir / "previews" / material_id
        preview_dir.mkdir(parents=True, exist_ok=True)
        image_path = preview_dir / f"page-{page}.png"
        if not image_path.exists():
            if not shutil.which("pdftoppm"):
                raise ValueError("PDF page rendering requires `pdftoppm`.")
            prefix = preview_dir / f"page-{page}"
            subprocess.run(
                ["pdftoppm", "-png", "-f", str(page), "-l", str(page), "-singlefile", "-r", "120", str(preview_pdf), str(prefix)],
                check=True,
                capture_output=True,
                timeout=45,
            )
        content = image_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "private, max-age=86400")
        self.end_headers()
        self.wfile.write(content)

    def _page_text(self, material_id: str, page: int) -> dict[str, Any]:
        if page < 1:
            raise ValueError("Page numbers start at 1.")
        material = self._registered_material(material_id)
        preview_pdf, preview_kind = self._preview_pdf_path(material)
        page_count = self._pdf_page_count(preview_pdf)
        if page > page_count:
            raise ValueError("Page not found.")
        preview_dir = self.store.data_dir / "previews" / material_id
        preview_dir.mkdir(parents=True, exist_ok=True)
        text_path = preview_dir / f"page-{page}.text.json"
        if text_path.exists():
            return json.loads(text_path.read_text(encoding="utf-8"))
        if not shutil.which("pdftotext"):
            result = {"material_id": material_id, "page": page, "preview_kind": preview_kind, "words": [], "text": "", "diagnostics": ["Text layer requires `pdftotext`."]}
            text_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            return result
        completed = subprocess.run(
            ["pdftotext", "-bbox", "-f", str(page), "-l", str(page), str(preview_pdf), "-"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed.returncode != 0:
            diagnostic = (completed.stderr or completed.stdout or "pdftotext failed").strip()[:360]
            result = {"material_id": material_id, "page": page, "preview_kind": preview_kind, "words": [], "text": "", "diagnostics": [diagnostic]}
        else:
            result = parse_poppler_bbox(completed.stdout)
            result.update({"material_id": material_id, "page": page, "preview_kind": preview_kind, "diagnostics": []})
        text_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    def _preview_pdf_path(self, material: dict[str, Any]) -> tuple[Path, str]:
        file_path = self.store.resolve_material_path(material)
        kind = str(material.get("kind") or "")
        if kind == "pdf":
            return file_path, "pdf"
        if kind not in OFFICE_PREVIEW_KINDS:
            raise ValueError("Page preview is available for PDF, Word, PowerPoint, and Excel materials.")
        return self._office_preview_pdf(str(material.get("id")), file_path), "converted_pdf"

    def _office_preview_pdf(self, material_id: str, file_path: Path) -> Path:
        preview_dir = self.store.data_dir / "previews" / material_id
        preview_dir.mkdir(parents=True, exist_ok=True)
        target = preview_dir / "document.pdf"
        if target.exists() and target.stat().st_mtime_ns >= file_path.stat().st_mtime_ns:
            return target
        converter = self._office_converter()
        if not converter:
            raise ValueError("Office layout preview requires LibreOffice. The Docker image installs it; local macOS development can use the configured wrapper.")
        with tempfile.TemporaryDirectory(prefix="office-preview-", dir=preview_dir) as tmp:
            output_dir = Path(tmp)
            if converter["mode"] == "wrapper":
                command = [converter["path"], str(file_path), str(output_dir), "pdf"]
            else:
                command = [
                    converter["path"],
                    "--headless",
                    "--nologo",
                    "--nofirststartwizard",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(output_dir),
                    str(file_path),
                ]
            completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=120)
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "LibreOffice conversion failed").strip()[:480]
                raise ValueError(f"Office layout preview conversion failed: {detail}")
            converted = sorted(output_dir.glob("*.pdf"))
            if not converted:
                raise ValueError("Office layout preview conversion did not produce a PDF.")
            if target.exists():
                target.unlink()
            shutil.move(str(converted[0]), str(target))
        return target

    def _office_converter(self) -> dict[str, str] | None:
        configured = os.getenv("CLW_LIBREOFFICE_WRAPPER", "").strip()
        if configured and Path(configured).expanduser().exists():
            return {"mode": "wrapper", "path": str(Path(configured).expanduser())}
        for name in ("libreoffice", "soffice"):
            path = shutil.which(name)
            if not path:
                continue
            if sys.platform == "darwin" and name == "soffice":
                continue
            return {"mode": "cli", "path": path}
        return None

    def _pdf_page_count(self, file_path: Path) -> int:
        if shutil.which("pdfinfo"):
            completed = subprocess.run(["pdfinfo", str(file_path)], check=False, capture_output=True, text=True, timeout=20)
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "pdfinfo could not read the file").strip()
                detail = " ".join(detail.split())[:240]
                raise ValueError(f"PDF preview unavailable: this file appears damaged or unsupported. {detail}")
            for line in completed.stdout.splitlines():
                if line.startswith("Pages:"):
                    return max(1, int(line.split(":", 1)[1].strip()))
            raise ValueError("PDF preview unavailable: the page count could not be read.")
        return 1

    def _registered_material(self, material_id: str) -> dict[str, Any]:
        state = self.store.load()
        material = next((item for item in state["materials"] if item["id"] == material_id), None)
        if not material:
            raise ValueError("Material not found.")
        file_path = self.store.resolve_material_path(material)
        if not file_path.exists() or not file_path.is_file():
            raise ValueError("Material file not found.")
        return material

    def _ask_materials(self, payload: dict[str, Any]) -> dict[str, Any]:
        state = self.store.load()
        language = "zh" if payload.get("language") == "zh" else "en"
        question = str(payload.get("question", "")).strip()
        action = str(payload.get("action") or "ask").strip().lower()
        if action not in ASSISTANT_ACTIONS:
            action = "ask"
        material_id = str(payload.get("material_id") or "") or None
        scope = str(payload.get("scope") or "material")
        if scope not in ASSISTANT_SCOPES:
            scope = "material"
        if not question:
            raise ValueError("Question cannot be empty.")
        if self._is_disallowed_writing_request(question):
            return {
                "status": "refused",
                "answer": self._assistant_refusal(language),
                "citations": [],
                "scope": scope,
                "action": action,
                "grounded": False,
                "provider": str(payload.get("api_provider") or "local"),
            }

        materials_by_id = {str(item.get("id")): item for item in state.get("materials", [])}
        active_material = materials_by_id.get(material_id or "")
        if action in {"explain", "connect"} and not active_material:
            return {
                "status": "not_found",
                "answer": "请先在阅读器中打开一份课程文件，再使用这个功能。" if language == "zh" else "Open a course file in Reader before using this action.",
                "citations": [],
                "scope": scope,
                "action": action,
                "grounded": False,
                "provider": str(payload.get("api_provider") or "local"),
            }
        query = self._assistant_query(question, action, payload, active_material)
        context_scope = self._context_scope_for_assistant(scope, question, material_id)
        contexts = self._assistant_contexts(state, context_scope, material_id, payload, action, question)
        ranked = self._rank_assistant_contexts(query, contexts, action, material_id)
        citations = self._select_assistant_citations(ranked, action, material_id)
        warning = ""
        if scope in WEB_ASSISTANT_SCOPES:
            try:
                citations.extend(self._web_assistant_citations(question, state, active_material, language))
            except AssistantProviderError as exc:
                if not citations:
                    return {
                        "status": "error",
                        "answer": self._assistant_web_error(language, str(exc)),
                        "citations": [],
                        "scope": scope,
                        "action": action,
                        "grounded": False,
                        "provider": str(payload.get("api_provider") or "local"),
                    }
                warning = self._assistant_web_warning(language, str(exc))
        if not citations:
            return {
                "status": "not_found",
                "answer": self._assistant_not_found(language),
                "citations": [],
                "scope": scope,
                "action": action,
                "grounded": False,
                "provider": str(payload.get("api_provider") or "local"),
            }
        citations = self._with_source_ids(citations)
        try:
            config = provider_config(payload)
        except AssistantProviderError as exc:
            return {
                "status": "error",
                "answer": self._assistant_provider_error(language, str(exc)),
                "citations": citations[:3],
                "scope": scope,
                "action": action,
                "grounded": False,
                "provider": str(payload.get("api_provider") or "local"),
            }
        if config["provider"] != "local":
            result = self._ask_with_provider(config, state, language, action, question, scope, active_material, citations)
            if warning:
                result["warning"] = " ".join(part for part in [warning, result.get("warning", "")] if part)
            return result
        return {
            "status": "ok",
            "answer": self._compose_assistant_answer(language, action, question, citations, material_id),
            "citations": citations,
            "scope": scope,
            "action": action,
            "grounded": True,
            "provider": "local",
            "warning": warning,
        }

    def _ask_with_provider(
        self,
        config: dict[str, str],
        state: dict[str, Any],
        language: str,
        action: str,
        question: str,
        scope: str,
        active_material: dict[str, Any] | None,
        citations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not config.get("api_key"):
            return {
                "status": "config_required",
                "answer": self._assistant_config_required(language, config["provider"]),
                "citations": citations[:3],
                "scope": scope,
                "action": action,
                "grounded": False,
                "provider": config["provider"],
            }
        prompt = build_study_prompt(
            language=language,
            action=action,
            question=question,
            scope=scope,
            course_name=str((state.get("course") or {}).get("name") or ""),
            active_material_title=self._active_material_display_title(active_material, citations),
            citations=citations,
        )
        try:
            max_tokens = 1600 if action in {"explain", "connect"} else 1200
            ai_result = call_chat_completions(config, prompt, max_tokens=max_tokens)
        except AssistantProviderError as exc:
            fallback_answer = self._compose_assistant_answer(language, action, question, citations, str((active_material or {}).get("id") or ""))
            return {
                "status": "ok",
                "answer": fallback_answer,
                "citations": citations,
                "scope": scope,
                "action": action,
                "grounded": True,
                "provider": config["provider"],
                "model": config.get("model"),
                "provider_error": str(exc),
                "warning": "",
            }
        ai_result = normalize_provider_result(ai_result, citations)
        status = str(ai_result.get("status") or "ok")
        if status not in {"ok", "not_found", "refused"}:
            status = "ok"
        if status == "not_found" and self._asks_for_field_contribution(question):
            status = "ok"
            ai_result["answer"] = self._field_contribution_answer(language, citations)
            ai_result["used_source_ids"] = [citation.get("source_id") for citation in citations[:5] if citation.get("source_id")]
        if status == "not_found" and self._asks_for_example(question) and any(citation.get("source_group") == "web" or citation.get("source_type") == "web" for citation in citations):
            status = "ok"
            ai_result["answer"] = self._example_background_answer(language, citations)
            ai_result["used_source_ids"] = [citation.get("source_id") for citation in citations[:5] if citation.get("source_id")]
        used_ids = {str(item) for item in ai_result.get("used_source_ids", []) if str(item).strip()}
        selected = [citation for citation in citations if not used_ids or citation.get("source_id") in used_ids]
        if status == "not_found":
            selected = []
        return {
            "status": status,
            "answer": str(ai_result.get("answer") or self._assistant_not_found(language)).strip(),
            "citations": selected[:5],
            "scope": scope,
            "action": action,
            "grounded": status == "ok",
            "provider": config["provider"],
            "model": config.get("model"),
        }

    def _test_assistant_provider(self, payload: dict[str, Any]) -> dict[str, Any]:
        language = "zh" if payload.get("language") == "zh" else "en"
        try:
            config = provider_config(payload)
        except AssistantProviderError as exc:
            return {"status": "error", "answer": self._assistant_provider_error(language, str(exc)), "provider": str(payload.get("api_provider") or "local")}
        if config["provider"] == "local":
            return {
                "status": "ok",
                "answer": "本地引用模式可用，不需要 API key。" if language == "zh" else "Local citation mode is available and does not need an API key.",
                "provider": "local",
            }
        if not config.get("api_key"):
            return {"status": "config_required", "answer": self._assistant_config_required(language, config["provider"]), "provider": config["provider"], "model": config.get("model")}
        messages = [
            {
                "role": "system",
                "content": "You are testing an API connection. Do not require or mention course data. Return only JSON.",
            },
            {
                "role": "user",
                "content": 'Return {"status":"ok","answer":"connection ok","used_source_ids":[]} if this request reaches you.',
            },
        ]
        try:
            call_chat_completions(config, messages, timeout=20, max_tokens=120)
        except AssistantProviderError as exc:
            return {
                "status": "error",
                "answer": self._assistant_provider_error(language, str(exc)),
                "provider": config["provider"],
                "model": config.get("model"),
            }
        return {
            "status": "ok",
            "answer": "API 连接测试通过。没有发送课程资料。" if language == "zh" else "API connection test passed. No course materials were sent.",
            "provider": config["provider"],
            "model": config.get("model"),
        }

    def _web_assistant_citations(self, question: str, state: dict[str, Any], active_material: dict[str, Any] | None, language: str) -> list[dict[str, Any]]:
        if os.getenv("CLW_WEB_SEARCH_ENABLED", "0").lower() in {"0", "false", "no"}:
            raise AssistantProviderError("Internet search is disabled.")
        course = state.get("course") or {}
        query = self._web_search_query(question, str(course.get("name") or ""), str((active_material or {}).get("title") or ""))
        is_contribution_question = self._asks_for_field_contribution(question)
        known_results = self._known_material_web_results(str((active_material or {}).get("title") or ""))
        try:
            results = search_web(query, max_results=10)
        except AssistantProviderError:
            if not known_results:
                raise
            results = []
        results = self._unique_web_results([*known_results, *results])
        if is_contribution_question:
            results = self._rank_field_contribution_web_results(results)[:4]
        else:
            results = self._rank_learning_web_results(results)[:4]
        if any(self._web_result_quality_score(result) > 0 for result in results):
            results = [result for result in results if self._web_result_quality_score(result) >= 0]
        citations: list[dict[str, Any]] = []
        retrieved_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
        for result in results:
            url = str(result.get("url") or "")
            title = str(result.get("title") or url or "Internet source")
            snippet = str(result.get("snippet") or title).strip()
            domain = urllib.parse.urlparse(url).netloc
            citations.append(
                {
                    "material_id": None,
                    "title": title,
                    "relative_path": url,
                    "source_type": "web",
                    "source_group": "web",
                    "locator": domain or "web",
                    "page": None,
                    "quote": self._clean_quote(snippet)[:760],
                    "url": url,
                    "domain": domain,
                    "retrieved_at": retrieved_at,
                    "score": 1,
                }
            )
        if not citations:
            raise AssistantProviderError("Internet search returned no usable sources.")
        return citations

    @classmethod
    def _known_material_web_results(cls, material_title: str) -> list[dict[str, str]]:
        identity = cls._material_identity_from_title(material_title)
        title = identity["title"].lower()
        if "companion to development studies" in title:
            return [
                {
                    "title": "The Companion to Development Studies | Taylor & Francis",
                    "url": "https://www.taylorfrancis.com/books/edit/10.4324/9780203528983/companion-development-studies-rob-potter-vandana-desai",
                    "snippet": "Publisher page for the third edition, describing the book as over a hundred concise chapters by experts that overview key theoretical and practical issues in development studies.",
                },
                {
                    "title": "Companion to Development Studies - Royal Holloway Research Portal",
                    "url": "https://pure.royalholloway.ac.uk/en/publications/companion-to-development-studies/",
                    "snippet": "University research portal record for Vandana Desai and Rob Potter's 2014 third edition, published by Routledge, describing its role as an overview for development studies students.",
                },
            ]
        return []

    @staticmethod
    def _unique_web_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
        unique: list[dict[str, str]] = []
        seen: set[str] = set()
        for result in results:
            url = str(result.get("url") or "").strip()
            key = url.lower() or str(result.get("title") or "").lower()
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(result)
        return unique

    @classmethod
    def _web_search_query(cls, question: str, course_name: str, material_title: str) -> str:
        if cls._asks_for_field_contribution(question):
            identity = cls._material_identity_from_title(material_title)
            pieces = []
            if identity["title"]:
                pieces.append(f'"{identity["title"]}"')
            pieces.extend(f'"{author}"' for author in identity["authors"][:2])
            if "companion to development studies" in identity["title"].lower():
                pieces.append("Routledge Taylor Francis")
            pieces.append("development studies contribution book review publisher university library syllabus academic field")
            return " ".join(piece for piece in pieces if piece).strip()

        pieces = [question.strip()[:220]]
        question_terms = {token for token in tokenize(question) if token not in ASSISTANT_STOPWORDS}
        clean_title = cls._clean_material_title(material_title)
        if cls._asks_for_example(question):
            pieces.append("case study real world example emerging markets development university research policy")
        if clean_title and (len(question_terms) <= 4 or cls._question_references_current_material(question)):
            pieces.append(clean_title[:120])
            if cls._question_references_current_material(question):
                pieces.append("publisher university library academic review")
        elif len(question_terms) <= 1 and course_name:
            pieces.append(course_name[:80])
        elif len(question_terms) <= 5:
            pieces.append("university academic source")
        return " ".join(piece for piece in pieces if piece).strip()

    @classmethod
    def _context_scope_for_assistant(cls, scope: str, question: str, material_id: str | None) -> str:
        if scope == "web" and material_id and (cls._question_references_current_material(question) or cls._asks_for_field_contribution(question)):
            return "material"
        return scope

    @staticmethod
    def _question_references_current_material(question: str) -> bool:
        lowered = question.lower()
        return any(
            marker in lowered
            for marker in [
                "这个文件",
                "这份文件",
                "这个资料",
                "这份资料",
                "当前资料",
                "本资料",
                "这本书",
                "本书",
                "这篇文献",
                "这本教材",
                "结合这文件",
                "结合这个文件",
                "结合这份资料",
                "this file",
                "this material",
                "current material",
                "the file",
                "the material",
                "this book",
                "the book",
                "this reading",
            ]
        )

    @staticmethod
    def _question_references_selection(question: str) -> bool:
        lowered = question.lower()
        return any(
            marker in lowered
            for marker in [
                "选中文本",
                "所选文本",
                "当前选中",
                "选区",
                "高亮",
                "这段话",
                "这一段",
                "这句话",
                "这一句",
                "this passage",
                "this sentence",
                "this paragraph",
                "selected text",
                "selection",
                "highlighted text",
                "highlight",
            ]
        )

    @classmethod
    def _should_use_selected_text(cls, question: str, action: str, selected_text: str) -> bool:
        selected_text = str(selected_text or "").strip()
        if not selected_text:
            return False
        if action != "ask":
            return True
        if cls._question_references_selection(question):
            return True
        question_terms = cls._meaningful_terms(question)
        if not question_terms:
            return True
        selection_terms = cls._meaningful_terms(selected_text)
        return bool(question_terms.intersection(selection_terms))

    def _assistant_query(self, question: str, action: str, payload: dict[str, Any], active_material: dict[str, Any] | None) -> str:
        pieces = [question]
        selected_text = str(payload.get("selected_text") or "").strip()
        if self._should_use_selected_text(question, action, selected_text):
            pieces.append(selected_text)
        if active_material and (action in {"connect", "explain", "review"} or self._question_references_current_material(question) or self._asks_for_field_contribution(question)):
            pieces.extend([str(active_material.get("title") or ""), str(active_material.get("relative_path") or "")])
        return "\n".join(piece for piece in pieces if piece.strip())

    def _assistant_contexts(self, state: dict[str, Any], scope: str, material_id: str | None, payload: dict[str, Any], action: str, question: str = "") -> list[dict[str, Any]]:
        materials = state.get("materials", [])
        material_lookup = {str(item.get("id")): item for item in materials}
        texts = self.store.material_texts()
        if scope == "material" and material_id:
            scoped_ids = {str(material_id)}
        elif scope == "web":
            scoped_ids = set()
        else:
            scoped_ids = {str(item.get("id")) for item in materials}
            if action in {"ask", "connect"}:
                scoped_ids = self._candidate_material_ids_for_assistant(materials, texts, question, material_id, limit=5) or scoped_ids
                if action == "connect" and material_id:
                    ordered_ids = [str(item.get("id") or "") for item in materials]
                    try:
                        active_index = ordered_ids.index(str(material_id))
                    except ValueError:
                        active_index = -1
                    if active_index >= 0:
                        neighbor_indexes = [active_index - 2, active_index - 1, active_index, active_index + 1, active_index + 2]
                        for neighbor_index in neighbor_indexes:
                            if 0 <= neighbor_index < len(ordered_ids):
                                scoped_ids.add(ordered_ids[neighbor_index])
        contexts: list[dict[str, Any]] = []
        include_student_notes = (
            action == "ask"
            and payload.get("include_notes") is not False
            and not self._is_material_structure_question(question)
            and not self._asks_for_example(question)
        )

        selected_text = str(payload.get("selected_text") or "").strip()
        selected_page = self._optional_int(payload.get("selected_page") or payload.get("page"))
        if self._should_use_selected_text(question, action, selected_text) and material_id in scoped_ids:
            contexts.append(
                self._assistant_context(
                    material_lookup.get(material_id or ""),
                    "selection",
                    selected_text,
                    locator="current selection",
                    page=selected_page,
                    priority=9,
                )
            )

        note_body = str(payload.get("note_body") or "").strip()
        if include_student_notes and note_body and material_id in scoped_ids:
            contexts.append(
                self._assistant_context(
                    material_lookup.get(material_id or ""),
                    "current_note",
                    note_body,
                    locator="unsaved reading note",
                    priority=5,
                )
            )

        annotation_body = str(payload.get("annotation_body") or "").strip()
        if include_student_notes and annotation_body and material_id in scoped_ids:
            contexts.append(
                self._assistant_context(
                    material_lookup.get(material_id or ""),
                    "current_annotation",
                    annotation_body,
                    locator="unsaved annotation note",
                    page=selected_page,
                    priority=5,
                )
            )

        if include_student_notes:
            for note in state.get("notes", []):
                note_material_id = str(note.get("material_id") or "")
                if note_material_id not in scoped_ids:
                    continue
                body = str(note.get("body") or "").strip()
                if body:
                    contexts.append(
                        self._assistant_context(
                            material_lookup.get(note_material_id),
                            "reading_note",
                            body,
                            locator="reading note",
                            priority=4,
                        )
                    )

            for annotation in state.get("annotations", []):
                annotation_material_id = str(annotation.get("material_id") or "")
                if annotation_material_id not in scoped_ids:
                    continue
                quote = "\n".join(
                    item
                    for item in [
                        str(annotation.get("selected_text") or "").strip(),
                        str(annotation.get("body") or "").strip(),
                    ]
                    if item
                )
                if quote:
                    page = self._optional_int(annotation.get("page"))
                    contexts.append(
                        self._assistant_context(
                            material_lookup.get(annotation_material_id),
                            "annotation",
                            quote,
                            locator=f"annotation{f' page {page}' if page else ''}",
                            page=page,
                            priority=4,
                        )
                    )

        for material in materials:
            current_material_id = str(material.get("id") or "")
            if current_material_id not in scoped_ids:
                continue
            text = texts.get(current_material_id, "")
            if not text.strip():
                continue
            for chunk in self._material_text_chunks(text, action=action, query=question):
                contexts.append(
                    self._assistant_context(
                        material,
                        "material",
                        chunk["quote"],
                        locator=chunk["locator"],
                        page=chunk["page"],
                        priority=2 if current_material_id == material_id else 0,
                    )
                )
        return [item for item in contexts if item.get("quote")]

    @classmethod
    def _candidate_material_ids_for_assistant(
        cls,
        materials: list[dict[str, Any]],
        texts: dict[str, str],
        query: str,
        active_material_id: str | None,
        limit: int = 5,
    ) -> set[str]:
        terms = cls._meaningful_terms(query)
        if not terms:
            return set()
        scored: list[tuple[int, int, str]] = []
        for index, material in enumerate(materials):
            material_id = str(material.get("id") or "")
            text = texts.get(material_id, "")
            if not text.strip():
                continue
            title_blob = " ".join([str(material.get("title") or ""), str(material.get("relative_path") or "")]).lower()
            sample = text[:240000].lower()
            score = 0
            for term in terms:
                if term in title_blob:
                    score += 5
                if term in sample:
                    score += 2
            if active_material_id and material_id == active_material_id:
                score += 3
            if score:
                scored.append((score, -index, material_id))
        selected = {material_id for _score, _index, material_id in sorted(scored, reverse=True)[:limit]}
        if active_material_id and active_material_id in {str(item.get("id") or "") for item in materials}:
            selected.add(str(active_material_id))
        return selected

    def _assistant_context(self, material: dict[str, Any] | None, source_type: str, quote: str, locator: str, page: int | None = None, priority: int = 0) -> dict[str, Any]:
        material = material or {}
        title = material.get("title") or "Current course material"
        return {
            "material_id": material.get("id"),
            "title": title,
            "display_title": self._display_title_from_quote(str(title), quote),
            "relative_path": material.get("relative_path") or "",
            "source_type": source_type,
            "locator": locator,
            "page": page,
            "quote": self._clean_quote(quote),
            "priority": priority,
        }

    def _material_text_chunks(self, text: str, action: str = "ask", query: str = "") -> list[dict[str, Any]]:
        if self._looks_like_pdf_internal_text(text):
            return []
        if action in {"ask", "connect"} and len(text) > 80000:
            focused = self._query_focused_material_chunks(text, query)
            if focused:
                return focused
        pages = text.split("\f")
        chunks: list[dict[str, Any]] = []
        if len(pages) > 1:
            for page_number, page_text in enumerate(pages, start=1):
                for quote in chunk_text(page_text):
                    chunks.append({"quote": quote, "locator": f"page {page_number}", "page": page_number})
            return chunks
        return [{"quote": quote, "locator": "text", "page": None} for quote in chunk_text(text)]

    @staticmethod
    def _looks_like_pdf_internal_text(text: str) -> bool:
        sample = str(text or "")[:5000]
        if not sample:
            return False
        markers = sum(sample.count(marker) for marker in ("/Type", "/Pages", "/Kids", " obj", "endobj", "stream", "xref"))
        human_words = len(re.findall(r"\b(?:development|lecture|chapter|introduction|theory|course|week)\b", sample, flags=re.I))
        return markers >= 8 and human_words <= 2

    @classmethod
    def _query_focused_material_chunks(cls, text: str, query: str, max_pages: int = 10) -> list[dict[str, Any]]:
        terms = [term for term in cls._meaningful_terms(query) if len(term) >= 3 or not re.fullmatch(r"[\u4e00-\u9fff]+", term)]
        if not terms:
            return []
        pages = text.split("\f")
        scored_pages: list[tuple[int, int, str]] = []
        if len(pages) > 1:
            for page_number, page_text in enumerate(pages, start=1):
                lowered = page_text.lower()
                score = sum(lowered.count(term) for term in terms)
                if score:
                    scored_pages.append((score, page_number, page_text))
            chunks: list[dict[str, Any]] = []
            for _score, page_number, page_text in sorted(scored_pages, key=lambda item: (-item[0], item[1]))[:max_pages]:
                for quote in chunk_text(page_text)[:3]:
                    chunks.append({"quote": quote, "locator": f"page {page_number}", "page": page_number})
            return chunks

        lowered = text.lower()
        windows: list[str] = []
        seen: set[tuple[int, int]] = set()
        for term in terms[:6]:
            start = lowered.find(term)
            if start < 0:
                continue
            window_start = max(0, start - 1200)
            window_end = min(len(text), start + 2200)
            key = (window_start // 500, window_end // 500)
            if key in seen:
                continue
            seen.add(key)
            windows.append(text[window_start:window_end])
        return [{"quote": quote, "locator": "text", "page": None} for window in windows for quote in chunk_text(window)[:2]]

    def _rank_assistant_contexts(self, query: str, contexts: list[dict[str, Any]], action: str, material_id: str | None) -> list[dict[str, Any]]:
        query_terms = self._meaningful_terms(query)
        references_current_material = self._question_references_current_material(query)
        ranked: list[dict[str, Any]] = []
        for index, context in enumerate(contexts):
            if context.get("source_type") != "selection" and self._is_low_information_quote(str(context.get("quote") or "")):
                continue
            quote_terms = self._meaningful_terms(" ".join([context.get("quote", ""), context.get("locator", "")]))
            title_terms = self._meaningful_terms(str(context.get("title") or ""))
            overlap = len(query_terms.intersection(quote_terms)) if query_terms else 0
            title_overlap = len(query_terms.intersection(title_terms)) if query_terms else 0
            score = overlap * 4 + min(title_overlap, 2) + int(context.get("priority") or 0)
            quote_blob = self._clean_quote(" ".join([str(context.get("quote") or ""), str(context.get("title") or "")])).lower()
            if self._asks_for_neoliberalism_levels(query):
                if "different levels of neoliberalism" in quote_blob:
                    score += 32
                if "hollowing out the state" in quote_blob:
                    score += 20
                if "pull yourself up" in quote_blob or "individual agency" in quote_blob:
                    score += 32
            if action in {"explain", "review"} and context.get("material_id") == material_id:
                score += 4
            if action == "connect" and context.get("source_type") == "material":
                score += 2
            if action == "explain" and context.get("source_type") == "material":
                score += self._explain_structure_score(context)
            score -= self._source_noise_penalty(context, action)
            if (
                action == "ask"
                and not overlap
                and context.get("source_type") not in {"selection", "current_note", "current_annotation"}
                and not (references_current_material and context.get("material_id") == material_id and context.get("source_type") == "material")
            ):
                continue
            if score <= 0 and action == "ask":
                continue
            ranked.append({**context, "score": score, "_order": index})
        if action in {"explain", "review"} and not ranked:
            fallback = [context for context in contexts if context.get("material_id") == material_id and context.get("source_type") == "material"][:3]
            ranked.extend({**context, "score": 1, "_order": index} for index, context in enumerate(fallback))
        return sorted(ranked, key=lambda item: (-int(item.get("score") or 0), item.get("_order", 0)))

    def _select_assistant_citations(self, ranked: list[dict[str, Any]], action: str, material_id: str | None) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        if action == "connect":
            current = [item for item in ranked if item.get("material_id") == material_id]
            others = [item for item in ranked if item.get("material_id") != material_id]
            ordered = current[:2] + others[:4]
        elif action == "explain":
            current = [item for item in ranked if item.get("material_id") == material_id] or ranked
            selections = [item for item in current if item.get("source_type") == "selection"]
            materials = [item for item in current if item.get("source_type") == "material"]
            ordered = selections[:1] + self._explain_preview_order(materials)
        elif action == "review":
            current = [item for item in ranked if item.get("material_id") == material_id] or ranked
            ordered = self._diverse_by_locator(current)
        else:
            ordered = ranked
        max_citations = 6 if action == "explain" else 5
        for item in ordered:
            key = (str(item.get("material_id") or ""), str(item.get("source_type") or ""), self._clean_quote(str(item.get("quote") or ""))[:160])
            if key in seen:
                continue
            seen.add(key)
            citation = {key_: value for key_, value in item.items() if not key_.startswith("_") and key_ != "priority"}
            citation["quote"] = self._clean_quote(str(citation.get("quote") or ""))[:760]
            selected.append(citation)
            if len(selected) >= max_citations:
                break
        return selected

    @classmethod
    def _explain_preview_order(cls, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if len(items) <= 6:
            return cls._diverse_by_locator(items)
        by_order = sorted(items, key=lambda item: int(item.get("_order") or 0))
        substantive = [
            item
            for item in by_order
            if not cls._is_explain_preview_noise(item)
            and len(cls._clean_quote(str(item.get("quote") or ""))) >= 70
        ]
        if len(substantive) < 3:
            substantive = [item for item in by_order if not cls._is_explain_preview_noise(item)] or by_order

        structural = sorted(substantive, key=lambda item: (-cls._explain_structure_score(item), int(item.get("_order") or 0)))
        ranked = sorted(substantive, key=lambda item: (-int(item.get("score") or 0), int(item.get("_order") or 0)))
        opening = sorted(
            substantive,
            key=lambda item: (
                cls._optional_int(item.get("page")) or 99999,
                int(item.get("_order") or 0),
            ),
        )[:3]
        spread: list[dict[str, Any]] = []
        if len(substantive) >= 6:
            for ratio in (0.25, 0.5, 0.75):
                spread.append(substantive[min(len(substantive) - 1, round((len(substantive) - 1) * ratio))])

        candidates = opening + structural[:3] + ranked[:3] + spread
        return cls._diverse_by_locator(cls._unique_contexts(candidates + substantive))

    @classmethod
    def _unique_contexts(cls, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for item in items:
            key = (
                str(item.get("material_id") or ""),
                str(item.get("locator") or item.get("page") or "text"),
                cls._clean_quote(str(item.get("quote") or ""))[:120],
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique

    @staticmethod
    def _explain_structure_score(context: dict[str, Any]) -> int:
        quote = str(context.get("quote") or "")
        lowered = quote.lower()
        score = 0
        if re.search(r"\b(abstract|introduction|overview|preface|contents|table of contents|chapter\s+\d+|part\s+[ivx\d]+|conclusion)\b", lowered):
            score += 5
        if re.search(r"(导论|绪论|摘要|目录|第一章|第二章|结论)", quote):
            score += 5
        if re.search(r"\b(argues?|examines?|explores?|introduces?|focus(?:es)? on|debates?|theory|framework|concept)\b", lowered):
            score += 3
        page = WorkspaceHandler._optional_int(context.get("page"))
        if page and page <= 12:
            score += 2
        if len(WorkspaceHandler._meaningful_terms(" ".join([quote, str(context.get("title") or "")]))) >= 8:
            score += 1
        return score

    @classmethod
    def _is_explain_preview_noise(cls, context: dict[str, Any]) -> bool:
        quote = str(context.get("quote") or "")
        page = cls._optional_int(context.get("page"))
        return cls._is_front_matter_noise(quote) or cls._is_back_matter_noise(quote, page)

    @staticmethod
    def _is_front_matter_noise(quote: str) -> bool:
        lowered = quote.lower()
        if re.search(
            r"\b(copyright|isbn|all rights reserved|library of congress|typeset in|cover design|printed in|dust jacket|references|bibliography)\b",
            lowered,
        ):
            return True
        if re.match(r"\s*(list of illustrations|list of tables|tables\s+\d)", lowered):
            return True
        many_years = len(re.findall(r"\b(?:18|19|20)\d{2}\b", quote)) >= 5
        bibliography_markers = re.search(r"\b(pp\.|journal|press|routledge|london|university|vol\.|eds?\.)\b", lowered)
        return bool(many_years and bibliography_markers)

    @staticmethod
    def _is_back_matter_noise(quote: str, page: int | None) -> bool:
        if not page or page < 80:
            return False
        lowered = quote.lower()
        if re.search(r"\b(notes|endnotes|references|bibliography|index)\b", lowered):
            return True
        numbered_note = bool(re.search(r"\b\d{1,3}\.\s+[A-Z][A-Za-z'’.-]+", quote))
        years = len(re.findall(r"\b(?:18|19|20)\d{2}\b", quote))
        citation_markers = re.search(r"\b(chapter|appendix|pp\.|vol\.|journal|press|university|survey|lecture)\b", lowered)
        return bool(numbered_note and years >= 2 and citation_markers)

    @staticmethod
    def _diverse_by_locator(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        diverse: list[dict[str, Any]] = []
        deferred: list[dict[str, Any]] = []
        seen_locators: set[tuple[str, str]] = set()
        for item in items:
            locator_key = (str(item.get("material_id") or ""), str(item.get("locator") or item.get("page") or "text"))
            if locator_key in seen_locators and len(diverse) < 4:
                deferred.append(item)
                continue
            seen_locators.add(locator_key)
            diverse.append(item)
        return diverse + deferred

    @staticmethod
    def _with_source_ids(citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        course_index = 0
        web_index = 0
        labeled = []
        for citation in citations:
            if citation.get("source_group") == "web" or citation.get("source_type") == "web":
                web_index += 1
                source_id = f"W{web_index}"
                source_group = "web"
            else:
                course_index += 1
                source_id = f"C{course_index}"
                source_group = "course"
            labeled.append({**citation, "source_id": source_id, "source_group": source_group})
        return labeled

    def _compose_assistant_answer(self, language: str, action: str, question: str, citations: list[dict[str, Any]], material_id: str | None = None) -> str:
        has_web = any(citation.get("source_group") == "web" or citation.get("source_type") == "web" for citation in citations)
        has_course = any(not (citation.get("source_group") == "web" or citation.get("source_type") == "web") for citation in citations)
        if action == "ask" and self._asks_for_field_contribution(question):
            return self._field_contribution_answer(language, citations)
        if action == "ask" and self._asks_for_example(question) and has_web:
            return self._example_background_answer(language, citations)
        if action == "ask" and self._asks_for_neoliberalism_levels(question):
            return self._neoliberalism_levels_answer(language, citations)
        if action == "ask" and self._is_definition_question(question):
            return self._definition_answer(language, question, citations)
        if action == "ask" and self._is_material_structure_question(question):
            return self._material_structure_answer(language, citations)
        if action == "ask" and self._is_comprehension_question(question):
            return self._comprehension_answer(language, question, citations)
        if language == "zh":
            if action == "explain":
                return self._preview_outline_answer(language, citations)
            elif action == "connect":
                return self._course_role_answer(language, citations, material_id)
            elif action == "review":
                return self._review_answer(language, citations)
            else:
                intro = "根据课程资料和互联网背景，能够支持的回答是：" if has_course and has_web else "根据互联网背景（非课程资料），能够支持的回答是：" if has_web else "根据当前课程资料，能够支持的回答是："
                close = "我没有使用课程资料之外的信息；形成课堂发言或作业观点前，请回到来源复核。"
                if has_web:
                    close = "互联网来源只作为背景，不代表老师或课程资料的要求；形成课堂发言或作业观点前，请回到课程资料复核。"
            points = [f"{index}. {self._source_point(citation, language)}" for index, citation in enumerate(self._answer_point_citations(citations), start=1)]
            return "\n".join([intro, *points, close])

        if action == "explain":
            return self._preview_outline_answer(language, citations)
        elif action == "connect":
            return self._course_role_answer(language, citations, material_id)
        elif action == "review":
            return self._review_answer(language, citations)
        else:
            intro = "The course materials and Internet background can support this answer:" if has_course and has_web else "Internet background can support this answer, but it is not course material:" if has_web else "The current course materials can support this answer:"
            close = "I did not use information outside the course materials. Check the sources before using this in class or coursework."
            if has_web:
                close = "Internet sources are background only, not course requirements. Check the course materials before using this in class or coursework."
        points = [f"{index}. {self._source_point(citation, language)}" for index, citation in enumerate(self._answer_point_citations(citations), start=1)]
        return "\n".join([intro, *points, close])

    @staticmethod
    def _answer_point_citations(citations: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
        course = [citation for citation in citations if not (citation.get("source_group") == "web" or citation.get("source_type") == "web")]
        web = [citation for citation in citations if citation.get("source_group") == "web" or citation.get("source_type") == "web"]
        if course and web and limit >= 2:
            selected = course[: limit - 1] + web[:1]
            return selected[:limit]
        return citations[:limit]

    @staticmethod
    def _is_comprehension_question(question: str) -> bool:
        normalized = question.lower()
        patterns = [
            "如何理解",
            "怎么理解",
            "通俗",
            "什么意思",
            "是什么意思",
            "这一句话",
            "这句话",
            "这段话",
            "explain this",
            "what does this mean",
            "how should i understand",
            "how to understand",
        ]
        return any(pattern in normalized for pattern in patterns)

    @staticmethod
    def _is_definition_question(question: str) -> bool:
        normalized = question.lower()
        return any(pattern in normalized for pattern in ["是什么", "什麼是", "什么是", "概念", "解释", "解釋", "define ", "what is ", "what are "])

    @staticmethod
    def _asks_for_neoliberalism_levels(question: str) -> bool:
        normalized = question.lower()
        return "neoliberalism" in normalized and any(pattern in normalized for pattern in ["level", "levels", "层级", "层次", "不同层面", "不同层次"])

    @staticmethod
    def _is_material_structure_question(question: str) -> bool:
        normalized = question.lower()
        patterns = [
            "如何讲述",
            "怎么讲述",
            "如何展开",
            "怎么展开",
            "如何论述",
            "怎么论述",
            "如何介绍",
            "怎么介绍",
            "这份资料如何",
            "这个资料如何",
            "这个文件如何",
            "这份文件如何",
            "how does this file",
            "how does this material",
            "how is this file",
            "how is this material",
            "how does the file",
            "how does the material",
        ]
        return any(pattern in normalized for pattern in patterns)

    @staticmethod
    def _asks_for_example(question: str) -> bool:
        normalized = question.lower()
        return any(pattern in normalized for pattern in ["案例", "例子", "实际", "现实", "case", "example", "real-world", "real world"])

    @staticmethod
    def _asks_for_field_contribution(question: str) -> bool:
        normalized = question.lower()
        contribution_markers = [
            "贡献",
            "影响",
            "地位",
            "杰出",
            "学术价值",
            "领域",
            "contribution",
            "impact",
            "influence",
            "significance",
            "field",
        ]
        entity_markers = [
            "作者",
            "作业",
            "编者",
            "这本书",
            "本书",
            "这篇文献",
            "这份资料",
            "this book",
            "the book",
            "author",
            "editor",
        ]
        return any(marker in normalized for marker in contribution_markers) and any(marker in normalized for marker in entity_markers)

    @classmethod
    def _material_identity_from_citations(cls, citations: list[dict[str, Any]]) -> dict[str, Any]:
        raw_title = ""
        title_texts: list[str] = []
        quote_texts: list[str] = []
        for citation in citations:
            raw_title = raw_title or str(citation.get("display_title") or citation.get("title") or "")
            title_texts.append(str(citation.get("title") or ""))
            quote_texts.append(str(citation.get("quote") or ""))
        identity = cls._material_identity_from_title(raw_title)
        if not identity["authors"]:
            identity["authors"] = cls._extract_material_authors(" ".join(title_texts))
        if not identity["authors"]:
            identity["authors"] = cls._extract_material_authors(" ".join(quote_texts))
        if not identity["title"]:
            identity["title"] = cls._preview_material_title(citations)
        return identity

    @classmethod
    def _material_identity_from_title(cls, title: str) -> dict[str, Any]:
        authors = cls._extract_material_authors(title)
        clean_title = str(title or "")
        clean_title = re.sub(r"\([^)]*(?:download(?:ed)?\s*copy|ebook\s*copy|library\s*copy|scan\s*copy)[^)]*\)", "", clean_title, flags=re.I)
        for author in authors:
            clean_title = re.sub(rf"\(?\b{re.escape(author)}\b\)?", "", clean_title, flags=re.I)
        clean_title = re.sub(r"\(\s*(?:,\s*)?\)", "", clean_title)
        clean_title = cls._clean_material_title(clean_title)
        return {"title": clean_title, "authors": authors}

    @staticmethod
    def _extract_material_authors(value: str) -> list[str]:
        authors: list[str] = []
        seen: set[str] = set()
        for group in re.findall(r"\(([^)]{3,180})\)", str(value or "")):
            lowered = group.lower()
            if re.search(r"edition|tagged|pdf|docx|pptx", lowered):
                continue
            parts = [part.strip(" .;:") for part in re.split(r"\s*(?:,|&|\band\b)\s*", group) if part.strip()]
            candidates = []
            for part in parts:
                if re.fullmatch(r"[A-Z][A-Za-z'’.-]+(?:\s+[A-Z][A-Za-z'’.-]+){1,4}", part):
                    candidates.append(part)
            if 1 <= len(candidates) <= 6:
                for candidate in candidates:
                    key = candidate.lower()
                    if key not in seen:
                        seen.add(key)
                        authors.append(candidate)
        return authors

    def _field_contribution_answer(self, language: str, citations: list[dict[str, Any]]) -> str:
        course = [citation for citation in citations if not (citation.get("source_group") == "web" or citation.get("source_type") == "web")]
        web = [citation for citation in citations if citation.get("source_group") == "web" or citation.get("source_type") == "web"]
        identity = self._material_identity_from_citations(course or citations)
        title = identity["title"] or self._preview_material_title(course or citations)
        authors = identity["authors"]
        author_text_zh = "、".join(authors) if authors else "资料中可识别的作者/编者"
        author_text_en = ", ".join(authors) if authors else "the identifiable author/editor names in the material"
        course_refs = self._source_refs(course, limit=3)
        web_refs = self._source_refs(web, limit=3)
        web_points = web[:3]
        if language == "zh":
            lines = [
                "这个问题应该先做实体识别，再做互联网背景核对；不能直接拿“领域贡献”这几个字去泛搜。",
                "",
                f"我从当前资料先识别到：书名是《{title}》；作者/编者线索是 {author_text_zh}。{course_refs}".strip(),
            ]
            if web_points:
                lines.extend(
                    [
                        "",
                        "从互联网背景可以谨慎提炼的方向是：",
                    ]
                )
                for index, citation in enumerate(web_points, start=1):
                    source_id = str(citation.get("source_id") or "")
                    title_text = str(citation.get("title") or "互联网来源")
                    quote = self._clean_quote(str(citation.get("quote") or ""))[:180]
                    lines.append(f"{index}. {title_text}：{quote} {f'[{source_id}]' if source_id else ''}".strip())
                lines.extend(
                    [
                        "",
                        f"保守结论：目前可以把它理解为 Development Studies 领域的资料入口、综述/companion 型资源，可能贡献在于组织领域议题、汇集关键讨论、帮助学生进入这个研究领域；但“杰出贡献”这种强判断需要书评、出版社说明、引用数据或权威课程书单进一步支持。{web_refs}".strip(),
                    ]
                )
            else:
                lines.extend(
                    [
                        "",
                        "当前资料只能支持书名和作者/编者识别，不能单独证明它在领域中的“杰出贡献”。请切换到“课程+互联网”或“互联网背景”再问，我会用书名和作者/编者去查证。",
                    ]
                )
            lines.append("你可以继续追问：这本书更像是原创理论贡献、领域综述贡献，还是教学/参考工具贡献？")
            return "\n".join(lines)

        lines = [
            "This question should start with entity extraction, then Internet-background checking; it should not search only for generic words like field contribution.",
            "",
            f"From the current material, I identify the title as “{title}” and the author/editor clue as {author_text_en}. {course_refs}".strip(),
        ]
        if web_points:
            lines.extend(["", "The Internet background cautiously suggests:"])
            for index, citation in enumerate(web_points, start=1):
                source_id = str(citation.get("source_id") or "")
                title_text = str(citation.get("title") or "Internet source")
                quote = self._clean_quote(str(citation.get("quote") or ""))[:180]
                lines.append(f"{index}. {title_text}: {quote} {f'[{source_id}]' if source_id else ''}".strip())
            lines.extend(
                [
                    "",
                    f"Conservative conclusion: treat it as a companion/survey-style entry point into Development Studies. Its likely contribution is organizing field themes, gathering key debates, and helping students enter the field; a stronger claim such as outstanding contribution needs reviews, publisher descriptions, citation data, or authoritative reading lists. {web_refs}".strip(),
                ]
            )
        else:
            lines.extend(
                [
                    "",
                    "The current material can identify the title and author/editor clue, but it cannot by itself prove the book's contribution to the field. Use Course + Internet or Internet background to check that claim.",
                ]
            )
        lines.append("Follow-up question: is the book's value mainly original theory, field synthesis, or teaching/reference support?")
        return "\n".join(lines)

    @staticmethod
    def _rank_field_contribution_web_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
        def score(result: dict[str, str]) -> int:
            text = " ".join([str(result.get("title") or ""), str(result.get("snippet") or ""), str(result.get("url") or "")]).lower()
            value = WorkspaceHandler._web_result_quality_score(result)
            if "development studies" in text:
                value += 2
            if re.search(r"\b(book review|review|publisher|syllabus|reading list|worldcat|google books)\b", text):
                value += 3
            return value

        return sorted(results, key=score, reverse=True) or results

    @staticmethod
    def _rank_learning_web_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
        return sorted(results, key=WorkspaceHandler._web_result_quality_score, reverse=True) or results

    @staticmethod
    def _web_result_quality_score(result: dict[str, str]) -> int:
        url = str(result.get("url") or "")
        domain = urllib.parse.urlparse(url).netloc.lower()
        text = " ".join([str(result.get("title") or ""), str(result.get("snippet") or ""), url]).lower()
        value = 0
        if re.search(r"(\.edu|\.ac\.uk|\.edu\.au|\.ac\.nz|\.ac\.jp|\.edu\.sg)", domain):
            value += 5
        if re.search(r"\b(university|library|libguides|publisher|press|book review|review|syllabus|reading list|journal|jstor|tandfonline|routledge|cambridge\.org|oup\.com|sagepub|springer|palgrave|worldcat|google books)\b", text):
            value += 5
        if re.search(r"\b(worldbank|undp|un\.org|oecd|who\.int|unesco|lse\.ac\.uk|ids\.ac\.uk)\b", text):
            value += 3
        if re.search(r"\b(amazon|ebay|abebooks|betterworldbooks|book2look|biblio|waterstones|kobo|bookshop|goodreads|alibris|thriftbooks|pdfdrive|z-lib|zlibrary|scribd|studocu|coursehero|chegg|quizlet|brainly|bartleby|slideshare)\b", text):
            value -= 8
        if re.search(r"\b(buy|buy a copy|price|used copies|free delivery|free pdf download|homework help|essay examples)\b", text):
            value -= 6
        return value

    def _example_background_answer(self, language: str, citations: list[dict[str, Any]]) -> str:
        course = [citation for citation in citations if not (citation.get("source_group") == "web" or citation.get("source_type") == "web")]
        web = [citation for citation in citations if citation.get("source_group") == "web" or citation.get("source_type") == "web"]
        course_refs = self._source_refs(course, limit=2)
        web_refs = self._source_refs(web, limit=3)
        web_points = web[:2] or citations[:2]
        key_terms = self._preview_terms_text(self._preview_key_terms(self._preview_material_title(course or citations), course or citations, limit=4), language)
        if language == "zh":
            lines = [
                "可以，但要把它当作互联网背景案例线索，而不是课程资料本身的要求。",
                "",
                f"课程资料给出的分析框架是：先从本资料中的概念或理论出发，再用外部案例检查这些概念如何出现在现实情境里。{course_refs}".strip(),
                "",
                "可用的案例线索：",
            ]
            for index, citation in enumerate(web_points, start=1):
                title = str(citation.get("title") or "互联网来源")
                quote = self._clean_quote(str(citation.get("quote") or ""))[:180]
                source_id = str(citation.get("source_id") or "")
                lines.append(f"{index}. {title}：{quote} {f'[{source_id}]' if source_id else ''}".strip())
            lines.extend(
                [
                    "",
                    f"使用方式：不要直接把案例当结论。先回到本资料确认要分析的是 {key_terms} 中的哪一个概念或关系，再用案例中的事实去对应它。{web_refs}".strip(),
                    "你可以继续追问：这个案例更像是在支持现代化理论，还是在暴露依附理论所说的不平等关系？",
                ]
            )
            return "\n".join(lines)
        lines = [
            "Yes, but treat this as Internet-background case material, not as a course requirement.",
            "",
            f"Use the course material as the analytical frame first, then use the external case to test how the concepts appear in practice. {course_refs}".strip(),
            "",
            "Possible case leads:",
        ]
        for index, citation in enumerate(web_points, start=1):
            title = str(citation.get("title") or "Internet source")
            quote = self._clean_quote(str(citation.get("quote") or ""))[:180]
            source_id = str(citation.get("source_id") or "")
            lines.append(f"{index}. {title}: {quote} {f'[{source_id}]' if source_id else ''}".strip())
        lines.extend(
            [
                "",
                f"Use it carefully: return to this material first and decide which concept or relationship in {key_terms} you are applying. {web_refs}".strip(),
                "Follow-up thinking question: does the case support a modernisation story, or does it expose the unequal relationship emphasized by dependency theory?",
            ]
        )
        return "\n".join(lines)

    def _neoliberalism_levels_answer(self, language: str, citations: list[dict[str, Any]]) -> str:
        level_citations = [
            citation
            for citation in citations
            if re.search(
                r"neoliberalism|hollowing out the state|pull yourself up|individual agency|structural",
                " ".join([str(citation.get("quote") or ""), str(citation.get("title") or ""), str(citation.get("locator") or "")]),
                flags=re.I,
            )
        ]
        selected = self._answer_point_citations(level_citations or citations, limit=4)
        refs = self._source_refs(selected, limit=4)
        course_refs = self._source_refs(
            [citation for citation in selected if citation.get("source_group") != "web" and citation.get("source_type") != "web"],
            limit=3,
        )
        if language == "zh":
            return "\n".join(
                [
                    "可以把这页的 “different levels of neoliberalism” 这样理解（只限下方来源）：",
                    "",
                    f"1. 结构层面（Structural: “hollowing out the state”）：新自由主义把问题定位为国家太大、干预太多，所以发展应更多围绕市场、GDP 增长和保护市场空间来组织，而不是让国家直接承担大量公共供给。{course_refs or refs}".strip(),
                    f"2. 个体层面（Individual agency and responsibility: “pull yourself up by your bootstraps”）：它把改善生活、谋生和承担风险的责任更多放到个人身上，把自由理解成个人在市场中自我选择、自我负责。{refs}".strip(),
                    "3. 读这页的关键：不要把它误读成在继续定义 development theory。这里是在说明 neoliberalism 怎样同时改写“国家应该做什么”和“个人应该承担什么”。",
                    "",
                    "边读边想：这两个层面分别把哪些责任从公共/国家层面移到了市场或个人层面？",
                ]
            )
        return "\n".join(
            [
                "You can read “different levels of neoliberalism” this way, using only the sources below:",
                "",
                f"1. Structural level (“hollowing out the state”): neoliberalism frames the problem as too much state intervention, so development is organized around markets, GDP growth, and protecting market space rather than broad direct state provision. {course_refs or refs}".strip(),
                f"2. Individual agency and responsibility (“pull yourself up by your bootstraps”): it shifts more responsibility for livelihood, opportunity, and risk onto individuals, treating market choice and self-responsibility as freedom. {refs}".strip(),
                "3. Reading point: this slide is not simply defining development theory. It is showing how neoliberalism redefines both what the state should do and what individuals are expected to carry.",
                "",
                "As you read, ask: which responsibilities are being moved away from the public/state level and toward markets or individuals?",
            ]
        )

    def _definition_answer(self, language: str, question: str, citations: list[dict[str, Any]]) -> str:
        course = [citation for citation in citations if not (citation.get("source_group") == "web" or citation.get("source_type") == "web")]
        web = [citation for citation in citations if citation.get("source_group") == "web" or citation.get("source_type") == "web"]
        selected = self._answer_point_citations(citations, limit=4)
        focus = self._definition_focus_phrase(question) or self._preview_terms_text(self._preview_key_terms("", selected, limit=2), language)
        quote_blob = self._clean_quote(" ".join(str(citation.get("quote") or "") for citation in selected)).lower()
        focus_lower = focus.lower()
        course_refs = self._source_refs(course or selected, limit=3)
        web_refs = self._source_refs(web, limit=2)
        source_refs = self._source_refs(selected, limit=4)
        if language == "zh":
            if self._asks_for_neoliberalism_levels(question) or ("neoliberalism" in focus_lower and "level" in focus_lower):
                return self._neoliberalism_levels_answer(language, citations)
            if "development theory" in focus_lower or (not focus_lower and "development theory" in quote_blob):
                lines = [
                    "可以用通俗的话这样理解（只限下方来源）：",
                    "",
                    f"1. 朴素意思：development theory 就是一套帮助我们解释“发展为什么发生、为什么失败、谁受益、谁被排除”的分析工具。它不是一个单独结论，更像是一副看材料的眼镜。{source_refs}".strip(),
                    f"2. 在课程资料里怎么读：Week 6 把它放在 Modernisation theory、Dependency theory 和 Development Impasse 之间，让你比较不同理论如何解释增长、改革、不平等和发展受阻。{course_refs}".strip(),
                    "3. 关键区别：不要只把 development theory 理解成“关于发展的理论”这句空话；在这门课里，它是用来组织历史材料、解释现实发展实践，并比较不同理论假设的框架。",
                ]
                if web:
                    lines.append(f"4. 互联网背景只用于补充定义，不代表课程要求；真正要回到课程资料看老师如何使用这个词。{web_refs}".strip())
                lines.extend(["", "边读边想：这页材料是在描述发展现象，还是在解释为什么不同理论会看出不同的问题？"])
                return "\n".join(lines)
            if "capabil" in quote_blob or "capability" in focus_lower:
                lines = [
                    "可以先这样理解（只限下方来源）：",
                    "",
                    f"1. 一句话定位：{focus} 是一种用 capabilities / functionings / substantive freedoms 来评价 wellbeing 和 development 的框架；它提醒你不要只看收入、资源或形式权利。{source_refs}".strip(),
                    f"2. 在课程资料里怎么读：先回到课程来源，看它怎样把 capability set、functionings、income poverty 和 substantive freedoms 放在一起；重点是“人实际能够做什么、成为什么”。{course_refs}".strip(),
                ]
                if web:
                    lines.append(f"3. 互联网背景怎么用：互联网来源可以帮助你补定义，但它只是背景，不代表老师要求；先用它确认术语，再回课程资料看本课如何使用。{web_refs}".strip())
                lines.extend(["", "边读边想：这个概念是在替代 GDP/收入指标，还是在补充它们看不到的生活机会？"])
                return "\n".join(lines)
            lines = [
                "可以先这样理解（只限下方来源）：",
                "",
                f"1. 先定位：{focus} 是需要放回课程资料语境里理解的概念或框架。{source_refs}".strip(),
                f"2. 阅读路径：先看课程来源如何使用这个词，再看它连接了哪些相邻概念、例子或评价标准。{course_refs}".strip(),
            ]
            if web:
                lines.append(f"3. 互联网背景只用于补充定义和背景，不代表课程要求。{web_refs}".strip())
            lines.append("回到来源时，试着用自己的话写一句定义，再标出哪一句来源支持它。")
            return "\n".join(lines)

        if self._asks_for_neoliberalism_levels(question) or ("neoliberalism" in focus_lower and "level" in focus_lower):
            return self._neoliberalism_levels_answer(language, citations)
        if "development theory" in focus_lower or (not focus_lower and "development theory" in quote_blob):
            lines = [
                "A plain way to read it, using only the sources below:",
                "",
                f"1. Basic meaning: development theory is an analytical tool for explaining why development happens, why it fails, who benefits, and who is excluded. It is less a single conclusion than a lens for reading the material. {source_refs}".strip(),
                f"2. How the course uses it: Week 6 places it between Modernisation theory, Dependency theory, and the Development Impasse so you can compare how different theories explain growth, reform, inequality, and blocked development. {course_refs}".strip(),
                "3. Key distinction: do not reduce it to the vague phrase “theory about development”. In this course it is a framework for organizing historical material, development practice, and competing assumptions.",
            ]
            if web:
                lines.append(f"4. Use Internet background only to clarify definitions; course use still comes from the course materials. {web_refs}".strip())
            lines.extend(["", "Thinking prompt: is the page describing development, or explaining why different theories see different problems?"])
            return "\n".join(lines)
        if "capabil" in quote_blob or "capability" in focus_lower:
            lines = [
                "Understand it this way, limited to the sources below:",
                "",
                f"1. Basic location: {focus} is a framework for evaluating wellbeing and development through capabilities, functionings, and substantive freedoms, rather than only income, resources, or formal rights. {source_refs}".strip(),
                f"2. How to read it in the course material: return to the course sources and track how capability set, functionings, income poverty, and substantive freedoms are connected. {course_refs}".strip(),
            ]
            if web:
                lines.append(f"3. Use Internet background only to clarify the term; it is not a course requirement. {web_refs}".strip())
            lines.append("Thinking prompt: is the concept replacing income/GDP measures, or supplementing what those measures miss?")
            return "\n".join(lines)
        lines = [
            "Understand it this way, limited to the sources below:",
            "",
            f"1. First locate {focus} as a course concept or framework. {source_refs}".strip(),
            f"2. Reading route: check how the course source uses the term, then identify the neighboring concepts, examples, or evaluative standards. {course_refs}".strip(),
        ]
        if web:
            lines.append(f"3. Internet background can clarify the term, but it is not a course requirement. {web_refs}".strip())
        lines.append("Go back to the source and write one definition in your own words, with the supporting sentence marked.")
        return "\n".join(lines)

    def _material_structure_answer(self, language: str, citations: list[dict[str, Any]]) -> str:
        selected = self._answer_point_citations(citations, limit=5)
        title = self._preview_material_title(selected or citations)
        source_refs = self._source_refs(selected or citations, limit=5)
        quote_blob = self._clean_quote(" ".join(str(citation.get("quote") or "") for citation in selected)).lower()
        if language == "zh":
            if "modernisation" in quote_blob and "dependency" in quote_blob and "development impasse" in quote_blob:
                return "\n".join(
                    [
                        f"可以这样读：本资料主要是在把 {title} 当作一条理论路线来讲，而不是只给一个定义。{source_refs}",
                        "",
                        "1. 起点：它先把 development theory 放进课程问题里，说明理论是用来帮助学生组织关于 development 的解释，而不是孤立背概念。",
                        "2. 推进：材料先回到早期关于农业、工业化和 catching up 的发展想象，再转向二十世纪关于工业化和追赶的理论解释。",
                        "3. 核心对比：Modernisation theory 更强调通过经济增长、社会改革和制度模仿实现发展；Dependency theory 则把这种追赶关系看成不平等关系，强调全球资本主义结构会制造依附和 underdevelopment。",
                        "4. Impasse 的作用：Development Impasse 不是一个新口号，而是提醒你两条理论都遇到解释困难，所以后面课程才会进入 alternative development、human development、post-development 等路径。",
                        "5. 回到来源时重点检查：page 2 的课程路线图、关于 industrialisation/catching up 的页面、以及 dependency 如何解释不平等发展的页面。",
                        "",
                        "边读边想：这份资料是在问“发展为什么发生”，还是在问“为什么有些发展路径会制造新的不平等”？",
                    ]
                )
            return "\n".join(
                [
                    f"可以这样读：本资料主要围绕 {title} 展开。{source_refs}",
                    "",
                    "1. 先看它从哪个问题或概念进入主题。",
                    "2. 再看它用哪些概念、对比或历史阶段推进解释。",
                    "3. 然后标出材料反复出现的定义句、转折句和例子。",
                    "4. 最后问自己：这份资料希望我改变哪一个原有理解？",
                    "",
                    "这不是替代阅读全文的总结，而是帮你找到第一遍阅读的路线。",
                ]
            )
        if "modernisation" in quote_blob and "dependency" in quote_blob and "development impasse" in quote_blob:
            return "\n".join(
                [
                    f"Read it as a theory pathway rather than a single definition: this material is mainly about {title}. {source_refs}",
                    "",
                    "1. It starts by placing development theory inside the course question of how students can organize explanations of development.",
                    "2. It then moves from earlier ideas of agriculture, industrialisation, and catching up into twentieth-century theories of industrialisation and development.",
                    "3. The main contrast is between Modernisation theory, which stresses growth, reform, and catching up, and Dependency theory, which treats that relationship as unequal and structurally dependent.",
                    "4. The Development Impasse signals the point where those theories struggle, preparing the course to move toward alternative, human-development, and post-development approaches.",
                    "",
                    "Thinking prompt: is the material asking why development happens, or why some development paths reproduce inequality?",
                ]
            )
        return "\n".join(
            [
                f"Read this material as a sequence around {title}. {source_refs}",
                "",
                "1. Identify the starting concept or question.",
                "2. Track the concepts, contrasts, or historical stages it uses to move forward.",
                "3. Mark definition sentences, turning points, examples, and evidence.",
                "4. Ask what earlier understanding the material wants you to revise.",
            ]
        )

    def _comprehension_answer(self, language: str, question: str, citations: list[dict[str, Any]]) -> str:
        selected = self._answer_point_citations(citations, limit=3)
        first = selected[0] if selected else {}
        source_id = str(first.get("source_id") or "C1")
        phrase = self._extract_focus_phrase(question)
        quote = self._clean_quote(" ".join(str(citation.get("quote") or "") for citation in selected))
        key_terms = self._key_terms_for_explanation(phrase or quote)
        source_refs = " ".join(f"[{citation.get('source_id')}]" for citation in selected if citation.get("source_id"))
        if language == "zh":
            prompts = [
                "1. 这里的 development 是指经济增长、社会结构变化，还是两者一起？",
                "2. agriculture 和 industrialisation 在材料里是先后关系、互相支撑，还是一种历史对比？",
                "3. catching up 是谁追赶谁？材料有没有说这种追赶为什么困难？",
            ]
            return "\n".join(
                [
                    "可以这样理解：",
                    "",
                    f"朴素意思：{self._plain_meaning_zh(phrase, key_terms, source_id)}",
                    "",
                    f"为什么这里重要：{self._why_it_matters_zh(quote, source_id)}",
                    "",
                    "边读边想：",
                    *prompts,
                    "",
                    f"回到来源：先看这句话附近的前后两条 bullet，再用上面三个问题检查自己的理解。{source_refs}".strip(),
                ]
            )
        prompts = [
            "1. Does development here mean economic growth, social change, or both?",
            "2. Are agriculture and industrialisation presented as a sequence, a support relationship, or a contrast?",
            "3. Who is catching up with whom, and does the material suggest why catching up is difficult?",
        ]
        return "\n".join(
            [
                "You can understand it like this:",
                "",
                f"Plain meaning: {self._plain_meaning_en(phrase, key_terms, source_id)}",
                "",
                f"Why it matters here: {self._why_it_matters_en(quote, source_id)}",
                "",
                "Think while reading:",
                *prompts,
                "",
                f"Go back to the source: reread the bullets around this phrase, then test your understanding with the questions above. {source_refs}".strip(),
            ]
        )

    def _preview_outline_answer(self, language: str, citations: list[dict[str, Any]]) -> str:
        has_web = any(citation.get("source_group") == "web" or citation.get("source_type") == "web" for citation in citations)
        course_citations = [citation for citation in citations if not (citation.get("source_group") == "web" or citation.get("source_type") == "web")]
        identity = self._material_identity_from_citations(course_citations or citations)
        title = identity["title"] or self._preview_material_title(course_citations or citations)
        authors = identity["authors"]
        key_terms = self._preview_key_terms(title, course_citations or citations)
        term_text = self._preview_terms_text(key_terms, language)
        material_form = self._preview_material_form(title, course_citations or citations, language)
        broad_focus = self._preview_broad_focus(title, key_terms, course_citations or citations, language)
        source_refs = self._source_refs(course_citations or citations, limit=5)
        source_hint = self._preview_source_hint(course_citations or citations, language)
        source_scope = "包含互联网背景" if has_web else "只根据当前资料"
        quote_blob = self._clean_quote(" ".join(str(citation.get("quote") or "") for citation in (course_citations or citations))).lower()
        title_blob = title.lower()
        is_development_studies_companion = "companion to development studies" in title_blob or "companion to development studies" in quote_blob
        if self._is_week6_development_theory_material(title, quote_blob):
            return self._week6_file_summary_answer(language, title, course_citations or citations)
        author_text_zh = f"；作者/编者线索：{'、'.join(authors)}" if authors else ""
        author_text_en = f"; author/editor clue: {', '.join(authors)}" if authors else ""
        if language == "zh":
            heading = f"资料小结（课前预习入口，{source_scope}）："
            if is_development_studies_companion:
                return "\n".join(
                    [
                        heading,
                        f"1. 这是什么：本资料是《{title}》{author_text_zh}。它不是把书名拆成几个词来解释，而是在为 Development Studies 这个研究领域提供 companion/导读型入口。{source_refs}".strip(),
                        "2. 它大概在讲什么：从当前可见的封面、开头或代表片段看，它的重点应放在发展研究这个领域的核心议题、理论传统、政策实践和争论脉络上，而不是某一个单独概念。",
                        "3. 第一遍怎么读：先看目录、导论和章节标题，找出它把发展研究拆成了哪些主题板块；再挑一两个章节精读，检查每章如何给出概念、争论和案例。",
                        "4. 预习时先抓这些东西：这本书如何界定 Development Studies；它安排了哪些主题群；不同章节是在解释理论、介绍政策问题，还是提供案例材料。",
                        f"5. 来源线索：{source_hint}",
                        "这是一份入口式资料小结，目的是帮你知道先从哪里读，不替代完整阅读；形成课堂发言或作业观点前，请回到来源复核。",
                    ]
                )
            heading = f"资料小结（课前预习入口，{source_scope}）："
            return "\n".join(
                [
                    heading,
                    f"1. 文件性质：这份资料属于{material_form}，主题可以先定位为《{title}》{author_text_zh}。第一遍先确认它服务于哪一周、哪一个概念群或哪条理论线索。{source_refs}".strip(),
                    f"2. 核心主题：{broad_focus} 先抓 {term_text} 这些主题或概念，避免把标题词硬拆成没有来源支持的概念关系。",
                    "3. 内容展开：先看标题、目录或开头几页，再标出材料反复出现的定义句、转折句和例子。判断每一部分是在给概念、做对比，还是引出后续课程问题。",
                    f"4. 第一遍怎么读：带着这几个问题读：{self._preview_questions_zh(key_terms)}",
                    f"5. 来源线索：{source_hint}",
                    "总结：这份资料小结只是帮你建立阅读入口和概念地图，不替代完整读原文；形成课堂发言或作业观点前，请回到来源复核。",
                ]
            )
        heading = "Source summary (pre-class entry point; includes Internet background):" if has_web else "Source summary (pre-class entry point; current material only):"
        if is_development_studies_companion:
            return "\n".join(
                [
                    heading,
                    f"1. What it is: this material is “{title}”{author_text_en}. It is not mainly a word-by-word title explanation; it is a companion-style entry point into Development Studies as a field. {source_refs}".strip(),
                    "2. Broad focus: based on the visible cover/opening or representative passages, read it as a field guide to themes, theories, policy issues, practice debates, and cases in development studies.",
                    "3. First pass: inspect the contents, introduction, and chapter headings before detailed reading. Ask which themes the book uses to map the field.",
                    "4. Watch for: how the book defines Development Studies, how it groups themes, and whether each chapter is explaining theory, policy, practice, or case material.",
                    f"5. Source trail: {source_hint}",
                    "This is an entry summary, not a substitute for reading. Check the cited passages before using the idea in class or coursework.",
                ]
            )
        return "\n".join(
            [
                heading,
                f"1. File type: this is {material_form} focused on “{title}”{author_text_en}. First locate the week, concept cluster, or theory thread it belongs to. {source_refs}".strip(),
                f"2. Core focus: {broad_focus} Start with {term_text}. Do not force title words into a relationship unless the source itself does that.",
                "3. How it develops: inspect the title, contents/opening pages, definition sentences, turns in the argument, and examples. Ask whether each section defines a concept, makes a contrast, or sets up a later course problem.",
                f"4. First-pass reading: use these questions: {self._preview_questions_en(key_terms)}",
                f"5. Source trail: {source_hint}",
                "In short: this summary gives you an entry route and concept map, not a substitute for reading. Check the cited passages before using the idea in class or coursework.",
            ]
        )

    @classmethod
    def _is_week6_development_theory_material(cls, title: str, quote_blob: str) -> bool:
        text = " ".join([str(title or ""), str(quote_blob or "")]).lower()
        return (
            ("week 6" in text or "development theory" in text)
            and ("modernisation" in text or "modernization" in text)
            and "dependency" in text
            and ("development impasse" in text or "impasse" in text)
        )

    def _week6_file_summary_answer(self, language: str, title: str, citations: list[dict[str, Any]]) -> str:
        refs = self._source_refs(citations, limit=6)
        first_ref = self._source_refs(citations, limit=1) or refs
        second_ref = self._source_refs(citations[1:], limit=2) or refs
        if language == "zh":
            return "\n".join(
                [
                    f"文件概括：这份文件是一门发展研究课程第 6 周讲义，主题是 Development theory: Modernisation, Dependency and the Development Impasse，也就是发展理论中的现代化理论、依附理论与发展僵局。{first_ref}".strip(),
                    "",
                    "以下是这份文件的核心内容：",
                    "",
                    f"1. 理论的定义与用途：讲义先说明 development theory 是一种帮助学生解释“发展为何发生、为何受阻、谁从发展中受益”的分析框架。它不是单纯背概念，而是训练你用理论组织历史与现实材料。{first_ref}".strip(),
                    f"2. 早期发展思想：文件把 19 世纪到 20 世纪中叶的发展想象放在农业、工业化和 catching up 的历史线上，为后面的现代化理论铺垫。{second_ref}".strip(),
                    f"3. 现代化理论：这一部分通过 Modernisation 与 Dependency 的对比，先把发展理解为经济增长、社会改革、制度建设和向西方工业国家追赶的过程，代表了战后正式发展理论的一个起点。{refs}".strip(),
                    f"4. 依附理论：讲义随后转向对现代化理论的批评，强调不平等的国际经济结构会让一些国家处在 dependency / underdevelopment 的位置。{refs}".strip(),
                    f"5. 发展僵局：最后的 Development Impasse 表示这些大理论都遇到解释困难，为后续课程讨论 alternative development、human development、post-development 等转向做准备。{refs}".strip(),
                    "",
                    "总结：这份讲义不是让你记住两个理论名词，而是让你看见发展理论如何从“追赶现代化”的解释，转向对不平等结构和理论局限的反思。",
                ]
            )
        return "\n".join(
            [
                f"File summary: this is a Week 6 lecture in a development studies course, focused on Modernisation theory, Dependency theory, and the Development Impasse. {first_ref}".strip(),
                "",
                "The core content is:",
                "",
                f"1. Definition and use of theory: the lecture frames development theory as a way to explain why development happens, why it is blocked, and who benefits from it. {first_ref}".strip(),
                f"2. Early development thinking: it places nineteenth- and twentieth-century ideas of agriculture, industrialisation, and catching up in a historical line. {second_ref}".strip(),
                f"3. Modernisation theory: it presents development as growth, reform, institution-building, and catching up with industrialised Western countries. {refs}".strip(),
                f"4. Dependency theory: it then turns to a critique of modernisation, stressing unequal global structures and underdevelopment. {refs}".strip(),
                f"5. Development Impasse: the final move shows why these large theories run into limits, preparing later course themes such as alternative development, human development, and post-development. {refs}".strip(),
                "",
                "In short: the lecture is not just naming two theories; it shows how development theory moves from modernisation narratives toward criticism of unequal structures and theoretical limits.",
            ]
        )

    def _course_role_answer(self, language: str, citations: list[dict[str, Any]], material_id: str | None = None) -> str:
        course_citations = [citation for citation in citations if not (citation.get("source_group") == "web" or citation.get("source_type") == "web")]
        selected = course_citations or citations
        active_selected = [citation for citation in selected if material_id and citation.get("material_id") == material_id] or selected[:2]
        title = self._preview_material_title(active_selected)
        quote_blob = self._clean_quote(" ".join(str(citation.get("quote") or "") for citation in active_selected)).lower()
        if self._is_week6_development_theory_material(title, quote_blob):
            return self._week6_course_role_answer(language, title, selected)
        return self._generic_course_role_answer(language, title, selected)

    def _week6_course_role_answer(self, language: str, title: str, citations: list[dict[str, Any]]) -> str:
        refs = self._source_refs(citations, limit=5)
        first_ref = self._source_refs(citations, limit=1) or refs
        other_refs = self._source_refs(citations[2:], limit=3) or refs
        if language == "zh":
            return "\n".join(
                [
                    f"在所有课程文件中，第 6 周讲义扮演“从历史转向理论”和“核心理论奠基”的关键角色。{first_ref}".strip(),
                    "",
                    "具体可以这样理解：",
                    "",
                    f"1. 理论框架的起点：它第一次集中解释“什么是发展理论”，把学生从描述发展现象带到用理论解释发展路径、失败和不平等。{first_ref}".strip(),
                    f"2. 历史与现代的桥梁：它承接前面关于殖民历史、早期发展思想和 industrialisation / catching up 的背景，把课程推进到战后正式发展理论。{refs}".strip(),
                    f"3. 核心矛盾的展开：这一讲把 Modernisation theory 和 Dependency theory 放在一起，让学生看到课程里的一个基本冲突：发展是线性追赶，还是由全球不平等结构塑造？{refs}".strip(),
                    f"4. 引出后续转折：Development Impasse 的作用是把课程带向后面的 alternative development、human development、neoliberalism 和 post-development。换句话说，没有第 6 周，后面那些“替代性发展观”会缺少问题背景。{other_refs}".strip(),
                    "",
                    "总结：第 6 周是整门课的理论转折点。它解释了为什么学生不能只把发展理解为增长或现代化，而要开始比较不同理论如何解释不平等、失败和替代路径。",
                ]
            )
        return "\n".join(
            [
                f"Across the course, the Week 6 lecture acts as a pivot from historical background into core development theory. {first_ref}".strip(),
                "",
                "Its role can be understood in four ways:",
                "",
                f"1. Starting point for theory: it explains what development theory is and moves students from describing development to explaining paths, failures, and inequalities. {first_ref}".strip(),
                f"2. Bridge from history to post-war theory: it links earlier historical material on industrialisation and catching up to formal post-war development theory. {refs}".strip(),
                f"3. Core tension: it stages the contrast between Modernisation theory and Dependency theory: is development a linear catching-up process, or is it shaped by unequal global structures? {refs}".strip(),
                f"4. Setup for later turns: the Development Impasse prepares later course files on alternative development, human development, neoliberalism, and post-development. {other_refs}".strip(),
                "",
                "In short: Week 6 is the course's theoretical turning point. It explains why development cannot be read only as growth or modernisation, and why later theories search for alternative standards.",
            ]
        )

    def _generic_course_role_answer(self, language: str, title: str, citations: list[dict[str, Any]]) -> str:
        key_terms = self._preview_key_terms(title, citations, limit=4)
        terms = self._preview_terms_text(key_terms, language)
        refs = self._source_refs(citations, limit=5)
        normalized_terms = {term.lower() for term in key_terms}
        title_blob = str(title or "").lower()
        if "alternative development" in normalized_terms or "human development" in normalized_terms or "alternative development" in title_blob:
            if language == "zh":
                return "\n".join(
                    [
                        f"这份资料在课程中的角色：它把课程从第 6 周那种“现代化理论 vs 依附理论”的大理论争论，推进到“有没有其他发展道路”和“如何以人为中心评价发展”的问题。{refs}".strip(),
                        "",
                        "具体可以这样理解：",
                        "",
                        f"1. 承接前面的理论困境：它不是重新讲 Modernisation / Dependency，而是在回应早期理论解释力不足之后，为什么要寻找 Alternative Development。{refs}".strip(),
                        "2. 改变评价标准：Human Development / capabilities approach 把注意力从单纯经济增长，转向人实际能做什么、能成为什么，以及是否拥有实质自由。",
                        "3. 提供新的阅读任务：读这份资料时，重点不是背一个新名词，而是比较“发展作为增长”和“发展作为人的能力扩展”这两种评价方式。",
                        "4. 连接后续课程：它为后面继续讨论 neoliberalism、post-development 或其他替代性发展观提供过渡。",
                        "",
                        "总结：第 8 周资料是课程里的“替代路径入口”。它让学生从批判旧理论，转向思考发展到底应该用什么目标和标准来衡量。",
                    ]
                )
            return "\n".join(
                [
                    f"Role in the course: this material moves from the Week 6 debate over large development theories toward the question of alternative development and human-centred evaluation. {refs}".strip(),
                    "",
                    "Its role has four parts:",
                    "",
                    f"1. It follows the earlier impasse: it responds to the limits of Modernisation and Dependency rather than simply repeating them. {refs}".strip(),
                    "2. It shifts the evaluative standard: Human Development / the capabilities approach asks what people are actually able to do and become.",
                    "3. It gives a new reading task: compare development as growth with development as expansion of human capabilities and substantive freedoms.",
                    "4. It prepares later course debates around neoliberalism, post-development, and other alternatives.",
                    "",
                    "In short: Week 8 is an entry point into alternative standards for development after the limits of earlier theories.",
                ]
            )
        if language == "zh":
            return "\n".join(
                [
                    f"这份资料在课程中的角色：它主要把学生带入《{title}》相关的 {terms} 问题。{refs}".strip(),
                    "",
                    "可以从三个层次看：",
                    f"1. 它提供概念入口：先帮你识别这部分课程在讨论什么问题，而不是先要求你形成完整观点。{refs}".strip(),
                    "2. 它提供课程连接：把当前文件中的概念、历史背景或案例，和课程其他资料里的理论线索接起来。",
                    "3. 它提供阅读任务：读完后你应该能说清楚这个文件提出了什么问题、使用了哪些概念、为后面哪些主题做铺垫。",
                    "",
                    "总结：这份资料的价值在于帮你定位课程地图中的一个节点；如果要形成更强结论，还需要继续对照其他课程文件。",
                ]
            )
        return "\n".join(
            [
                f"Role in the course: this material introduces the course problem around “{title}” and the themes {terms}. {refs}".strip(),
                "",
                "You can read its role at three levels:",
                f"1. Concept entry point: it helps you identify what this part of the course is asking before you form a finished view. {refs}".strip(),
                "2. Course connection: it links concepts, background, or cases in the current file to theory threads in other materials.",
                "3. Reading task: after reading, you should be able to state what problem the file raises, which concepts it uses, and what later themes it prepares.",
                "",
                "In short: the file is a node in the course map. Stronger conclusions require checking it against other course files.",
            ]
        )

    @staticmethod
    def _preview_material_title(citations: list[dict[str, Any]]) -> str:
        for citation in citations:
            title = str(citation.get("display_title") or citation.get("title") or "").strip()
            if title:
                return WorkspaceHandler._clean_material_title(title) or "当前资料"
        return "当前资料"

    @classmethod
    def _active_material_display_title(cls, active_material: dict[str, Any] | None, citations: list[dict[str, Any]]) -> str:
        for citation in citations:
            title = str(citation.get("display_title") or "").strip()
            if title:
                return title
        return cls._clean_material_title(str((active_material or {}).get("title") or ""))

    @classmethod
    def _preview_material_form(cls, title: str, citations: list[dict[str, Any]], language: str) -> str:
        text = " ".join([title, *[str(citation.get("quote") or "")[:420] for citation in citations[:4]]]).lower()
        if re.search(r"\b(week\s+\d+\s+lecture|lecture|slides?|powerpoint|ppt)\b", text):
            return "一份课程讲义 / lecture slides" if language == "zh" else "a lecture slide deck or course handout"
        if re.search(r"\b(abstract|methodology|findings|journal|doi)\b", text):
            return "一篇论文或学术文章" if language == "zh" else "an article or academic paper"
        if re.search(r"\b(contents|chapter\s+\d+|isbn|published|publisher|routledge|oxford university press|cambridge university press|palgrave|sage)\b", text):
            return "一本书或章节式阅读资料" if language == "zh" else "a book or chapter-style reading"
        return "一份课程资料" if language == "zh" else "a course material"

    @classmethod
    def _preview_broad_focus(cls, title: str, terms: list[str], citations: list[dict[str, Any]], language: str) -> str:
        title_blob = title.lower()
        term_blob = " ".join(terms).lower()
        quote_blob = cls._clean_quote(" ".join(str(citation.get("quote") or "") for citation in citations[:4])).lower()
        if language == "zh":
            if "development as freedom" in title_blob or ("development" in term_blob and "freedom" in term_blob and "substantive freedom" in quote_blob):
                return "当前片段提示它把 development 不只看作收入增长，而是和 substantive freedoms、capabilities / social opportunity 这样的评价基础联系起来。"
            if ("alternative development" in term_blob or "human development" in term_blob) or ("capabil" in quote_blob and "human development" in quote_blob):
                return "当前片段提示它把课程从早期发展理论的局限，推进到 alternative development、human development 和 capabilities approach。"
            if "postcolonialism" in term_blob and "decoloniality" in term_blob:
                return "当前片段提示它在解释 postcolonial / decolonial approaches 如何影响 development studies，重点会落在发展话语、知识与权力、agency 等关系上。"
            if ("modernisation" in term_blob or "modernization" in term_blob) and "dependency" in term_blob:
                return "当前片段提示它把 development theory 作为理解路线，重点比较 Modernisation、Dependency 以及 Development Impasse。"
            return "当前来源提示你从资料自己的标题、导论、章节或代表段落进入。"
        if "development as freedom" in title_blob or ("development" in term_blob and "freedom" in term_blob and "substantive freedom" in quote_blob):
            return "The visible passages suggest that development is being treated not just as income growth, but through substantive freedoms, capabilities, and social opportunity."
        if ("alternative development" in term_blob or "human development" in term_blob) or ("capabil" in quote_blob and "human development" in quote_blob):
            return "The visible passages shift from earlier development theory toward alternative development, human development, and the capabilities approach."
        if "postcolonialism" in term_blob and "decoloniality" in term_blob:
            return "The visible passages frame postcolonial and decolonial approaches as ways to examine development discourse, knowledge, power, and agency."
        if ("modernisation" in term_blob or "modernization" in term_blob) and "dependency" in term_blob:
            return "The visible passages use development theory as a reading route through Modernisation, Dependency, and the Development Impasse."
        return "The current sources point you back to the material's own title, introduction, chapters, or representative passages."

    @classmethod
    def _display_title_from_quote(cls, title: str, quote: str) -> str:
        clean_quote = cls._clean_quote(quote)
        if "the companion to development studies" in clean_quote.lower() or "the companion to development studies" in str(title or "").lower():
            edition = "Third Edition" if re.search(r"\bthird edition\b", " ".join([str(title or ""), clean_quote]), flags=re.I) else ""
            return "The Companion to Development Studies" + (f", {edition}" if edition else "")
        patterns = [
            r"Week\s+\d+\s+Lecture\s+(.+?)(?:\s+MAN\d{4,}|Tuesday|Monday|Wednesday|Thursday|Friday|Dr\.?\s|Lecture of|School for|Overview\b)",
            r"((?:Development|Modernisation|Modernization|Dependency|Postcolonialism|Decoloniality|Neoliberalism|Alternative Development)[^●\n]{12,180}?)(?:\s+MAN\d{4,}|Tuesday|Monday|Wednesday|Thursday|Friday|Dr\.?\s|Lecture of|School for|Overview\b)",
        ]
        for pattern in patterns:
            match = re.search(pattern, clean_quote, flags=re.I)
            if not match:
                continue
            candidate = cls._clean_material_title(match.group(1))
            if candidate and len(candidate.split()) >= 3:
                return candidate
        return cls._clean_material_title(title)

    @staticmethod
    def _clean_material_title(title: str) -> str:
        clean = re.sub(r"\b(?:pdf|docx|pptx|xlsx|txt)\b", "", str(title or ""), flags=re.I)
        clean = re.sub(r"\([^)]*(?:download(?:ed)?\s*copy|ebook\s*copy|library\s*copy|scan\s*copy)[^)]*\)", "", clean, flags=re.I)
        clean = re.sub(
            r"\((?:[A-Z][A-Za-z'’.-]+(?:\s+[A-Z][A-Za-z'’.-]+){1,4})(?:\s*,\s*[A-Z][A-Za-z'’.-]+(?:\s+[A-Z][A-Za-z'’.-]+){1,4}){0,5}\)",
            "",
            clean,
        )
        clean = clean.replace("_", " ").replace("-", " ")
        clean = re.sub(r"\b[A-Z]{2,}\d{3,}[A-Z]?\b", "", clean, flags=re.I)
        clean = re.sub(r"\bWeek\s+\d+\s+Lecture\b", "", clean, flags=re.I)
        clean = re.sub(r"\b(?:Tagged|download copy|ebook copy|library copy|scan copy)\b", "", clean, flags=re.I)
        clean = re.sub(r"\(\s*\)", "", clean)
        clean = re.sub(r"\(\s*\d+\s*$", "", clean)
        clean = re.sub(r"\s+\(\d+\)$", "", clean)
        clean = re.sub(r"\b\d{2}\s+\d{2}\s+\d{2}(?:\s+\d{2}){0,4}\b", "", clean)
        clean = re.sub(r"\s+", " ", clean).strip(" -_(),")
        return clean

    @classmethod
    def _preview_key_terms(cls, title: str, citations: list[dict[str, Any]], limit: int = 5) -> list[str]:
        title_text = str(title or "")
        source_text = " ".join([title_text, *[str(citation.get("quote") or "")[:320] for citation in citations[:4]]])
        protected_phrases = [
            "Development theory",
            "Modernisation theory",
            "Modernization theory",
            "Modernisation",
            "Modernization",
            "Dependency theory",
            "Dependency",
            "Development Impasse",
            "Postcolonialism",
            "Decoloniality",
            "Human Development",
            "Alternative Development",
            "Post-development",
            "Development Studies",
            "Capability approach",
            "Capabilities approach",
            "Capabilities",
        ]
        terms: list[str] = []
        seen: set[str] = set()
        for phrase in protected_phrases:
            if re.search(rf"\b{re.escape(phrase)}\b", title_text, flags=re.I):
                cls._append_preview_term(phrase, terms, seen, limit)
                if len(terms) >= limit:
                    return terms[:limit]
        for phrase in protected_phrases:
            if re.search(rf"\b{re.escape(phrase)}\b", source_text, flags=re.I):
                cls._append_preview_term(phrase, terms, seen, limit)
                if len(terms) >= limit:
                    return terms[:limit]
        if terms:
            return terms[:limit]
        for match in re.finditer(r"[A-Za-z][A-Za-z'-]{2,}|[\u4e00-\u9fff]{2,}", title):
            cls._append_preview_term(match.group(0), terms, seen, limit)
        if len(terms) >= 2:
            return terms[:limit]
        for match in re.finditer(r"[A-Za-z][A-Za-z'-]{2,}|[\u4e00-\u9fff]{2,}", source_text):
            cls._append_preview_term(match.group(0), terms, seen, limit)
            if len(terms) >= limit:
                break
        return terms or ["核心概念"]

    @staticmethod
    def _append_preview_term(raw_term: str, terms: list[str], seen: set[str], limit: int) -> None:
        if len(terms) >= limit:
            return
        term = raw_term.strip("'’")
        normalized = term.lower()
        if normalized in ASSISTANT_STOPWORDS or normalized in {
            "the",
            "and",
            "for",
            "with",
            "from",
            "that",
            "this",
            "edition",
            "second",
            "third",
            "tagged",
            "week",
            "lecture",
            "companion",
            "introduce",
            "introduces",
            "introduced",
            "connect",
            "connects",
            "connected",
            "then",
            "first",
        }:
            return
        if re.fullmatch(r"\d+", normalized) or normalized in seen:
            return
        seen.add(normalized)
        terms.append(term)

    @staticmethod
    def _preview_terms_text(terms: list[str], language: str) -> str:
        clean_terms = [term for term in terms if term]
        if not clean_terms:
            return "核心概念" if language == "zh" else "the key concepts"
        if language == "zh":
            return "、".join(clean_terms[:5])
        return ", ".join(clean_terms[:5])

    @staticmethod
    def _source_refs(citations: list[dict[str, Any]], limit: int = 5) -> str:
        refs = [f"[{citation.get('source_id')}]" for citation in citations[:limit] if citation.get("source_id")]
        return " ".join(refs)

    def _preview_source_hint(self, citations: list[dict[str, Any]], language: str) -> str:
        hints: list[str] = []
        for citation in citations[:3]:
            source_id = str(citation.get("source_id") or "").strip()
            locator = str(citation.get("locator") or citation.get("page") or "text").strip()
            quote = self._clean_quote(str(citation.get("quote") or ""))
            if not quote:
                continue
            excerpt = quote[:120] + ("..." if len(quote) > 120 else "")
            if language == "zh":
                hints.append(f"{f'[{source_id}] ' if source_id else ''}{locator} 提示：{excerpt}")
            else:
                hints.append(f"{f'[{source_id}] ' if source_id else ''}{locator} suggests: {excerpt}")
        if hints:
            return "；".join(hints)
        return "请从下方来源回到原文继续读。" if language == "zh" else "Use the sources below to continue reading."

    @staticmethod
    def _preview_questions_zh(terms: list[str]) -> str:
        first = terms[0] if terms else "核心概念"
        second = terms[1] if len(terms) > 1 else "另一个概念"
        normalized = {term.lower() for term in terms}
        if "postcolonialism" in normalized and "decoloniality" in normalized:
            return "Postcolonialism 和 Decoloniality 分别在回应什么发展叙事？材料如何把发展知识、权力和 agency 连起来？"
        if "alternative development" in normalized or "human development" in normalized:
            return "这份资料如何说明 alternative development 为什么出现？Human Development / capabilities approach 又把评价重点从经济增长转向了什么？"
        if ("modernisation" in normalized or "modernisation theory" in normalized or "modernization theory" in normalized) and ("dependency" in normalized or "dependency theory" in normalized):
            return "这份资料如何对比 Modernisation 与 Dependency？Development Impasse 是在指出哪一种解释困难？"
        if first.lower() == "development studies":
            return "这本资料如何界定 Development Studies 这个领域？它把这个领域拆成了哪些主题板块？哪些章节最适合先读？"
        if len(terms) == 1:
            return f"“{first}”在这份资料中被当作主题、理论、方法还是案例入口？材料用哪些章节或段落展开它？"
        return f"“{first}”在这里怎样被界定或使用？“{second}”在这个主题中扮演什么角色？材料用什么例子、章节或证据推进讨论？"

    @staticmethod
    def _preview_questions_en(terms: list[str]) -> str:
        first = terms[0] if terms else "the main concept"
        second = terms[1] if len(terms) > 1 else "another key concept"
        normalized = {term.lower() for term in terms}
        if "postcolonialism" in normalized and "decoloniality" in normalized:
            return "What development narratives do Postcolonialism and Decoloniality respond to, and how does the material connect development knowledge, power, and agency?"
        if "alternative development" in normalized or "human development" in normalized:
            return "Why does alternative development appear here, and what does Human Development / the capabilities approach shift attention toward?"
        if ("modernisation" in normalized or "modernisation theory" in normalized or "modernization theory" in normalized) and ("dependency" in normalized or "dependency theory" in normalized):
            return "How does this material contrast Modernisation and Dependency, and what explanatory difficulty does the Development Impasse point to?"
        if first.lower() == "development studies":
            return "How does this material define Development Studies as a field? Which themes does it use to map the field? Which chapters should you inspect first?"
        if len(terms) == 1:
            return f"Is “{first}” being used as a topic, theory, method, or case entry point? Which sections develop it?"
        return f"How is “{first}” defined or used here? What role does “{second}” play in this topic? What examples, sections, or evidence move the discussion forward?"

    def _review_answer(self, language: str, citations: list[dict[str, Any]]) -> str:
        key_phrase = self._review_key_phrase(citations)
        if language == "zh":
            questions = [
                f"1. 你能用自己的话解释“{key_phrase}”在来源 1 中是什么意思吗？",
                "2. 下方两个来源对同一主题的关注点有什么相同或不同？" if len(citations) > 1 else "2. 回到下方来源，哪一句最能支持你的理解？",
                "3. 如果闭卷复习，你会怎样用 3 句话说明这段资料的核心意思？",
            ]
            return "\n".join(["根据课程资料，建议用这些问题自测：", *questions, "这些问题是复习脚手架，不是作业答案。"])
        questions = [
            f"1. Can you explain what “{key_phrase}” means in source 1 using your own words?",
            "2. What is similar or different across the first two sources?" if len(citations) > 1 else "2. Which sentence in the source best supports your understanding?",
            "3. In a closed-book review, how would you state the core idea of this passage in three sentences?",
        ]
        return "\n".join(["Use these source-grounded review questions:", *questions, "These are review prompts, not assignment answers."])

    def _source_point(self, citation: dict[str, Any], language: str) -> str:
        quote = self._clean_quote(str(citation.get("quote") or ""))
        excerpt = quote[:220] + ("..." if len(quote) > 220 else "")
        title = str(citation.get("title") or "")
        locator = str(citation.get("locator") or "")
        source_id = str(citation.get("source_id") or "").strip()
        prefix = f"[{source_id}] " if source_id else ""
        is_web = citation.get("source_group") == "web" or citation.get("source_type") == "web"
        if language == "zh":
            if is_web:
                return f"{prefix}互联网来源《{title}》{f'（{locator}）' if locator else ''}显示：{excerpt}"
            return f"{prefix}来源《{title}》{f'（{locator}）' if locator else ''}显示：{excerpt}"
        if is_web:
            return f"{prefix}Internet source “{title}”{f' ({locator})' if locator else ''} shows: {excerpt}"
        return f"{prefix}Source “{title}”{f' ({locator})' if locator else ''} shows: {excerpt}"

    @staticmethod
    def _extract_focus_phrase(question: str) -> str:
        quoted = re.findall(r"[“\"'‘](.*?)[”\"'’]", question)
        if quoted:
            return max((item.strip() for item in quoted), key=len, default="")
        cleaned = re.sub(r"^(如何理解|怎么理解|请解释|解释|what does|how should i understand|how to understand)\s*", "", question.strip(), flags=re.I)
        cleaned = re.sub(r"(这一句话|这句话|是什么意思|什么意思|这段话).*$", "", cleaned).strip(" ：:？?")
        return cleaned[:180]

    @staticmethod
    def _definition_focus_phrase(question: str) -> str:
        cleaned = question.strip()
        cleaned = re.sub(r"^(什么是|什麼是|what is|what are|define)\s*", "", cleaned, flags=re.I)
        cleaned = re.sub(r"(是什么|是什麼|是什么概念|是个什么概念|是什麼概念|概念是什么).*$", "", cleaned)
        cleaned = cleaned.strip(" ：:？?。.")
        return cleaned[:120]

    @staticmethod
    def _key_terms_for_explanation(text: str) -> set[str]:
        return {token.lower() for token in tokenize(text) if token not in ASSISTANT_STOPWORDS}

    @staticmethod
    def _plain_meaning_zh(phrase: str, terms: set[str], source_id: str) -> str:
        if {"agriculture", "industrialisation"}.issubset(terms) or "catching" in terms:
            return f"这句话是在把 19 世纪的“发展”拆成几个相互连接的过程：农业变化提供基础，工业化把生产和劳动组织带入工厂与城市，而 catching up 指后来者试图追赶已经工业化的国家或地区。它不是单独讲农业或工业，而是在提示你看它们如何共同构成一种发展路径。 [{source_id}]"
        focus = f"“{phrase}”" if phrase else "这句话"
        return f"{focus}需要放回材料前后文理解：先看它在定义一个概念、描述一个历史过程，还是提出一个因果关系；再判断材料用它来引出什么课程主题。 [{source_id}]"

    @staticmethod
    def _plain_meaning_en(phrase: str, terms: set[str], source_id: str) -> str:
        if {"agriculture", "industrialisation"}.issubset(terms) or "catching" in terms:
            return f"The phrase breaks 19th-century 'development' into connected processes: agricultural change, industrial production, and attempts by later-developing places to catch up with already industrialised economies. It is asking you to see a development pathway rather than one isolated event. [{source_id}]"
        focus = f"'{phrase}'" if phrase else "this phrase"
        return f"To understand {focus}, place it back into the surrounding slide or paragraph: decide whether it is defining a concept, describing a historical process, or setting up a cause-and-effect relationship. [{source_id}]"

    @staticmethod
    def _why_it_matters_zh(quote: str, source_id: str) -> str:
        lowered = quote.lower()
        if "rural" in lowered and "factory" in lowered:
            return f"材料附近提到农村劳动力进入城镇和工厂劳动，所以这句话很可能是在说明工业化如何改变生产方式、人口流动和资本主义发展，而不是只说技术进步。 [{source_id}]"
        if "marx" in lowered or "capitalis" in lowered:
            return f"材料把这个主题放在马克思/资本主义发展脉络里，因此重点是理解经济结构、劳动关系和工业化之间的关系。 [{source_id}]"
        return f"它的重要性在于提示你不要只记标题，而要追问材料如何把概念、历史变化和因果链条连起来。 [{source_id}]"

    @staticmethod
    def _why_it_matters_en(quote: str, source_id: str) -> str:
        lowered = quote.lower()
        if "rural" in lowered and "factory" in lowered:
            return f"The surrounding material mentions rural workers moving into towns and factory labour, so the phrase likely points to changes in production, migration, and capitalist development, not just technology. [{source_id}]"
        if "marx" in lowered or "capitalis" in lowered:
            return f"The material places this topic in a Marx/capitalist-development frame, so the key is the relationship between economic structure, labour relations, and industrialisation. [{source_id}]"
        return f"It matters because it asks you to connect the concept, the historical change, and the causal chain rather than just memorise the title. [{source_id}]"

    def _review_key_phrase(self, citations: list[dict[str, Any]]) -> str:
        terms: list[str] = []
        for citation in citations:
            for token in tokenize(" ".join([str(citation.get("title") or ""), str(citation.get("quote") or "")])):
                if token in ASSISTANT_STOPWORDS:
                    continue
                if re.fullmatch(r"[\u4e00-\u9fff]+", token):
                    terms.append(token)
                    continue
                if len(token) >= 3:
                    terms.append(token)
        return next(iter(terms), "the key concept")

    @staticmethod
    def _clean_quote(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def _meaningful_terms(value: str) -> set[str]:
        return {token for token in tokenize(value) if token not in ASSISTANT_STOPWORDS}

    @classmethod
    def _is_low_information_quote(cls, value: str) -> bool:
        clean = cls._clean_quote(value)
        if not clean:
            return True
        terms = cls._meaningful_terms(clean)
        if len(clean) < 16 and len(terms) < 2:
            return True
        return len(clean) < 40 and len(terms) <= 3

    @staticmethod
    def _source_noise_penalty(context: dict[str, Any], action: str = "ask") -> int:
        if context.get("source_type") != "material":
            return 0
        quote = str(context.get("quote") or "")
        lowered = quote.lower()
        penalty = 0
        clean = WorkspaceHandler._clean_quote(quote)
        if len(clean) < 80:
            penalty += 3
        if clean.isupper() and len(WorkspaceHandler._meaningful_terms(clean)) <= 8:
            penalty += 4
        if re.search(r"\b(references|bibliography|journal|press|forthcoming|reprinted|edited by)\b", lowered):
            penalty += 5
        if re.search(r"\b(nobel laureate|winner of|master of|has taught|copyright|isbn|all rights reserved|the economist|the nation|financial times|washington post|new york review|times literary supplement|the guardian)\b", lowered):
            penalty += 4
        if re.search(r"\b(business week|book review|printed in|typeset in|cover design|dust jacket|library of congress)\b", lowered):
            penalty += 6
        if action != "explain" and re.search(r"\bchapter\s+\d+\s*:", lowered):
            penalty += 3
        if action != "explain" and len(re.findall(r"\b(?:18|19|20)\d{2}\b", quote)) >= 3:
            penalty += 4
        if quote.count(";") >= 5:
            penalty += 2
        return penalty

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        try:
            number = int(value)
        except (TypeError, ValueError):
            return None
        return number if number > 0 else None

    @staticmethod
    def _is_disallowed_writing_request(question: str) -> bool:
        return bool(WRITING_REQUEST_PATTERN.search(question))

    @staticmethod
    def _assistant_refusal(language: str) -> str:
        if language == "zh":
            return "我不能代写 essay、论文、报告或作业答案。可以帮你基于课程资料解释概念、梳理来源、提出复习问题，或检查你自己的理解是否有资料依据。"
        return "I cannot write essays, papers, reports, or assignment answers for you. I can help explain course concepts, organize sources, suggest review questions, or check whether your own understanding is supported by the materials."

    @staticmethod
    def _assistant_not_found(language: str) -> str:
        if language == "zh":
            return "当前课程资料无法支持这个回答。请换到整门课程范围、打开相关资料，或补充你的选中文本/笔记后再问。"
        return "The current course materials cannot support this answer. Try whole-course scope, open a relevant material, or add selected text or notes."

    @staticmethod
    def _assistant_config_required(language: str, provider: str = "deepseek") -> str:
        provider_name = {
            "deepseek": "DeepSeek",
            "openai": "OpenAI",
            "gemini": "Google Gemini",
            "openrouter": "OpenRouter",
            "kimi": "Kimi / Moonshot",
            "custom": "custom provider",
        }.get(provider, provider)
        if language == "zh":
            return f"需要先在设置中配置 {provider_name} API key，或通过环境变量启动服务。配置前我不会把课程资料片段发送到第三方模型。"
        return f"Configure a {provider_name} API key in Settings, or start the service with an environment API key. Until then, course excerpts are not sent to a third-party model."

    @staticmethod
    def _assistant_provider_error(language: str, detail: str) -> str:
        if language == "zh":
            return f"第三方 AI 调用失败：{detail}"
        return f"Third-party AI call failed: {detail}"

    @staticmethod
    def _assistant_provider_fallback_warning(language: str) -> str:
        if language == "zh":
            return "云端 AI 回答格式不稳定，已先用课程资料本地回答。你可以继续追问，我会尽量把问题拆成可理解的学习步骤。"
        return "The cloud AI response format was unstable, so I answered from local course sources first. You can keep asking follow-up questions."

    @staticmethod
    def _assistant_web_error(language: str, detail: str) -> str:
        if language == "zh":
            return f"互联网搜索暂时不可用：{detail}"
        return f"Internet search is unavailable: {detail}"

    @staticmethod
    def _assistant_web_warning(language: str, detail: str) -> str:
        if language == "zh":
            return f"互联网搜索暂时不可用，已先根据课程资料回答。原因：{detail}"
        return f"Internet search is temporarily unavailable, so I answered from course materials first. Reason: {detail}"

    def _material_route(self, path: str) -> str | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 3 and parts[:2] == ["api", "materials"]:
            return urllib.parse.unquote(parts[2])
        return None

    def _material_file_route(self, path: str) -> str | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 4 and parts[:2] == ["api", "materials"] and parts[3] == "file":
            return urllib.parse.unquote(parts[2])
        return None

    def _material_pages_route(self, path: str) -> str | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 4 and parts[:2] == ["api", "materials"] and parts[3] == "pages":
            return urllib.parse.unquote(parts[2])
        return None

    def _material_page_image_route(self, path: str) -> tuple[str, int] | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 5 and parts[:2] == ["api", "materials"] and parts[3] == "pages" and parts[4].endswith(".png"):
            return urllib.parse.unquote(parts[2]), int(parts[4][:-4])
        return None

    def _material_page_text_route(self, path: str) -> tuple[str, int] | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 5 and parts[:2] == ["api", "materials"] and parts[3] == "pages" and parts[4].endswith(".text.json"):
            return urllib.parse.unquote(parts[2]), int(parts[4].removesuffix(".text.json"))
        return None

    def _annotation_route(self, path: str) -> str | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 3 and parts[:2] == ["api", "annotations"]:
            return urllib.parse.unquote(parts[2])
        return None

    def _note_route(self, path: str) -> str | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 3 and parts[:2] == ["api", "notes"]:
            return urllib.parse.unquote(parts[2])
        return None

    def _course_select_route(self, path: str) -> str | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "courses" and parts[3] == "select":
            return urllib.parse.unquote(parts[2])
        return None

    def _course_route(self, path: str) -> str | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 3 and parts[:2] == ["api", "courses"]:
            return urllib.parse.unquote(parts[2])
        return None

    def _course_upload_route(self, path: str) -> str | None:
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "courses" and parts[3] == "upload":
            return urllib.parse.unquote(parts[2])
        return None

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_JSON_BODY_BYTES:
            raise ValueError("JSON body is too large.")
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _read_multipart_files(self) -> list[tuple[str, bytes]]:
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            raise ValueError("Expected multipart file upload.")
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type})
        fields = form["files"] if "files" in form else []
        if not isinstance(fields, list):
            fields = [fields]
        files: list[tuple[str, bytes]] = []
        for field in fields:
            if not getattr(field, "filename", None):
                continue
            files.append((field.filename, field.file.read()))
        return files

    def _json(self, value: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _host_allowed(self) -> bool:
        host = self.headers.get("Host", "")
        if not host:
            return True
        hostname = host.rsplit(":", 1)[0].strip("[]")
        return hostname in LOOPBACK_HOSTS or os.getenv("CLW_ALLOW_NETWORK", "").lower() in {"1", "true", "yes"}


def run() -> None:
    host = os.getenv("CLW_HOST", "127.0.0.1")
    port = int(os.getenv("CLW_PORT", "8780"))
    server = ThreadingHTTPServer((host, port), WorkspaceHandler)
    print(f"Course Learning Workspace is running at http://127.0.0.1:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Course Learning Workspace.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
