from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

from .materials import scan_folder, stable_id


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str, fallback: str = "course") -> str:
    value = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value.strip().lower(), flags=re.UNICODE)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or fallback


def safe_filename(value: str) -> str:
    name = Path(value).name.strip()
    name = re.sub(r"[\\/:*?\"<>|]+", "-", name)
    return name or "material"


class WorkspaceStore:
    def __init__(self, data_dir: str | Path | None = None):
        default_dir = Path(os.getenv("CLW_DATA_DIR", "")) if os.getenv("CLW_DATA_DIR") else Path(__file__).resolve().parents[1] / "data"
        self.data_dir = Path(data_dir) if data_dir else default_dir
        self.text_dir = self.data_dir / "extracted-text"
        self.courses_dir = self.data_dir / "courses"
        self.state_path = self.data_dir / "workspace.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.text_dir.mkdir(parents=True, exist_ok=True)
        self.courses_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return self.empty_state()
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return self.empty_state()
        return self.normalize_state(state)

    def save(self, state: dict[str, Any]) -> dict[str, Any]:
        state = self.normalize_state(state)
        state["updated_at"] = utc_now()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return state

    def create_course(self, name: str) -> dict[str, Any]:
        state = self.load()
        clean_name = name.strip() or "New Course"
        course_id = stable_id(clean_name, utc_now())
        folder = self.unique_course_folder(clean_name)
        folder.mkdir(parents=True, exist_ok=True)
        course = {
            "id": course_id,
            "name": clean_name,
            "source_path": str(folder),
            "folder_path": str(folder),
            "materials_seen": 0,
            "materials_parsed": 0,
            "materials_failed": 0,
            "materials": [],
            "notes": [],
            "annotations": [],
            "units": [],
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        state["courses"].insert(0, course)
        state["active_course_id"] = course_id
        return self.save(state)

    def select_course(self, course_id: str) -> dict[str, Any]:
        state = self.load()
        if not self.course_by_id(state, course_id):
            raise ValueError("Course not found.")
        state["active_course_id"] = course_id
        return self.save(state)

    def rename_course(self, course_id: str, name: str) -> dict[str, Any]:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Course name cannot be empty.")
        state = self.load()
        course = self.require_course(state, course_id)
        course["name"] = clean_name
        course["updated_at"] = utc_now()
        return self.save(state)

    def upload_materials(self, course_id: str, files: list[tuple[str, bytes]]) -> dict[str, Any]:
        if not files:
            raise ValueError("No files were selected.")
        state = self.load()
        course = self.require_course(state, course_id)
        course_dir = self.resolve_course_folder(course)
        course_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in files:
            target = self.unique_file_path(course_dir / safe_filename(filename))
            target.write_bytes(content)
        return self.rescan_course(course_id)

    def create_unit(self, course_id: str, name: str) -> dict[str, Any]:
        state = self.load()
        course = self.require_course(state, course_id)
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Unit name cannot be empty.")
        unit_id = stable_id(course_id, clean_name, utc_now())
        folder_name = self.unique_unit_folder(course, clean_name)
        unit = {"id": unit_id, "name": clean_name, "folder_name": folder_name, "created_at": utc_now()}
        course.setdefault("units", []).append(unit)
        Path(course["folder_path"], folder_name).mkdir(parents=True, exist_ok=True)
        return self.save(state)

    def assign_materials_to_unit(self, course_id: str, unit_id: str, material_ids: list[str]) -> dict[str, Any]:
        state = self.load()
        course = self.require_course(state, course_id)
        unit = next((item for item in course.get("units", []) if item["id"] == unit_id), None)
        if not unit:
            raise ValueError("Learning unit not found.")
        course_dir = self.resolve_course_folder(course)
        unit_dir = course_dir / unit["folder_name"]
        unit_dir.mkdir(parents=True, exist_ok=True)
        selected = {str(material_id) for material_id in material_ids}
        for material in list(course.get("materials", [])):
            if material["id"] not in selected:
                continue
            source = self.resolve_material_path(material, course)
            if not source.exists() or not source.is_file():
                continue
            target = self.unique_file_path(unit_dir / source.name)
            if source.resolve() != target.resolve():
                shutil.move(str(source), str(target))
        return self.rescan_course(course_id)

    def rescan_course(self, course_id: str) -> dict[str, Any]:
        state = self.load()
        course = self.require_course(state, course_id)
        course_folder = self.resolve_course_folder(course)
        scanned_course, materials, texts = scan_folder(course_folder)
        merged_course = {
            **course,
            **scanned_course,
            "id": course["id"],
            "name": course["name"],
            "folder_path": str(course_folder),
            "source_path": str(course_folder),
            "units": course.get("units", []),
            "notes": course.get("notes", []),
            "annotations": course.get("annotations", []),
            "updated_at": utc_now(),
        }
        merged_course["materials"] = materials
        course.update(merged_course)
        for material_id, text in texts.items():
            self.text_path(material_id).write_text(text, encoding="utf-8")
        keep_ids = {material["id"] for item in state["courses"] for material in item.get("materials", [])}
        keep_ids.update(texts)
        for text_file in self.text_dir.glob("*.txt"):
            if text_file.stem not in keep_ids:
                text_file.unlink(missing_ok=True)
        return self.save(state)

    def replace_scan(self, course: dict[str, Any], materials: list[dict[str, Any]], texts: dict[str, str]) -> dict[str, Any]:
        state = self.load()
        active = self.active_course(state)
        if not active:
            state = self.create_course(str(course.get("name") or "Course"))
            active = self.active_course(state)
        assert active is not None
        active.update({**course, "id": active["id"], "name": course.get("name") or active["name"], "folder_path": course.get("source_path")})
        active["materials"] = materials
        active.setdefault("notes", [])
        active.setdefault("annotations", [])
        for material_id, text in texts.items():
            self.text_path(material_id).write_text(text, encoding="utf-8")
        return self.save(state)

    def material_text(self, material_id: str) -> str:
        path = self.text_path(material_id)
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")

    def material_texts(self) -> dict[str, str]:
        state = self.load()
        material_ids = {material["id"] for material in state.get("materials", [])}
        return {
            path.stem: path.read_text(encoding="utf-8", errors="ignore")
            for path in self.text_dir.glob("*.txt")
            if path.stem in material_ids
        }

    def add_note(self, material_id: str | None, body: str, language: str = "en") -> dict[str, Any]:
        state = self.load()
        active = self.active_course(state)
        if not active:
            raise ValueError("Create or select a course before saving notes.")
        notes = active.setdefault("notes", [])
        note = {
            "id": f"note-{len(notes) + 1:04d}",
            "material_id": material_id,
            "type": "reading_note",
            "body": body.strip(),
            "language": "zh" if language == "zh" else "en",
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        if not note["body"]:
            raise ValueError("Note body cannot be empty.")
        notes.insert(0, note)
        self.save(state)
        return note

    def update_note(self, note_id: str, body: str, language: str = "en") -> dict[str, Any]:
        state = self.load()
        active = self.active_course(state)
        if not active:
            raise ValueError("Create or select a course before updating notes.")
        note = next((item for item in active.setdefault("notes", []) if item.get("id") == note_id), None)
        if not note:
            raise ValueError("Note not found.")
        clean_body = body.strip()
        if not clean_body:
            raise ValueError("Note body cannot be empty.")
        note.update(
            {
                "type": "reading_note",
                "body": clean_body,
                "language": "zh" if language == "zh" else "en",
                "updated_at": utc_now(),
            }
        )
        self.save(state)
        return note

    def delete_note(self, note_id: str) -> dict[str, Any]:
        state = self.load()
        active = self.active_course(state)
        if not active:
            raise ValueError("Create or select a course before deleting notes.")
        notes = active.setdefault("notes", [])
        for index, note in enumerate(notes):
            if note.get("id") == note_id:
                removed = notes.pop(index)
                self.save(state)
                return removed
        raise ValueError("Note not found.")

    def add_annotation(self, payload: dict[str, Any]) -> dict[str, Any]:
        state = self.load()
        active = self.active_course(state)
        if not active:
            raise ValueError("Create or select a course before saving annotations.")
        material_id = str(payload.get("material_id") or "").strip()
        if not any(item.get("id") == material_id for item in active.get("materials", [])):
            raise ValueError("Material not found.")
        target_type = str(payload.get("target_type") or "text").strip()
        if target_type not in {"text", "region", "image"}:
            raise ValueError("Unsupported annotation target.")
        style = str(payload.get("style") or "comment").strip()
        if style not in {"highlight", "underline", "strike", "comment"}:
            raise ValueError("Unsupported annotation style.")
        body = str(payload.get("body") or payload.get("comment") or "").strip()
        selected_text = str(payload.get("selected_text") or "").strip()
        rects = self.normalized_rects(payload.get("rects", []))
        if target_type == "region" and not rects:
            raise ValueError("Region annotations need a selected page area.")
        if not body and not selected_text and not rects:
            raise ValueError("Annotation needs a comment or selected text.")
        annotations = active.setdefault("annotations", [])
        annotation = {
            "id": self.next_annotation_id(annotations),
            "material_id": material_id,
            "type": "annotation",
            "target_type": target_type,
            "style": style,
            "page": self.optional_positive_int(payload.get("page")),
            "rects": rects,
            "selected_text": selected_text,
            "body": body,
            "language": "zh" if payload.get("language") == "zh" else "en",
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        annotations.insert(0, annotation)
        self.save(state)
        return annotation

    def update_annotation(self, annotation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        state = self.load()
        active = self.active_course(state)
        if not active:
            raise ValueError("Create or select a course before updating annotations.")
        annotation = next((item for item in active.setdefault("annotations", []) if item.get("id") == annotation_id), None)
        if not annotation:
            raise ValueError("Annotation not found.")
        target_type = str(payload.get("target_type", annotation.get("target_type") or "text")).strip()
        if target_type not in {"text", "region", "image"}:
            raise ValueError("Unsupported annotation target.")
        style = str(payload.get("style", annotation.get("style") or "comment")).strip()
        if style not in {"highlight", "underline", "strike", "comment"}:
            raise ValueError("Unsupported annotation style.")
        body = str(payload.get("body", annotation.get("body") or "")).strip()
        selected_text = str(payload.get("selected_text", annotation.get("selected_text") or "")).strip()
        rects = self.normalized_rects(payload.get("rects", annotation.get("rects", [])))
        page = self.optional_positive_int(payload.get("page", annotation.get("page")))
        if target_type in {"region", "image"} and not rects:
            raise ValueError("Area annotations need a selected page area.")
        if not body and not selected_text and not rects:
            raise ValueError("Annotation needs a comment or selected text.")
        annotation.update(
            {
                "target_type": target_type,
                "style": style,
                "page": page,
                "rects": rects,
                "selected_text": selected_text,
                "body": body,
                "language": "zh" if payload.get("language", annotation.get("language")) == "zh" else "en",
                "updated_at": utc_now(),
            }
        )
        self.save(state)
        return annotation

    def delete_annotation(self, annotation_id: str) -> dict[str, Any]:
        state = self.load()
        active = self.active_course(state)
        if not active:
            raise ValueError("Create or select a course before deleting annotations.")
        annotations = active.setdefault("annotations", [])
        for index, annotation in enumerate(annotations):
            if annotation.get("id") == annotation_id:
                removed = annotations.pop(index)
                self.save(state)
                return removed
        raise ValueError("Annotation not found.")

    def text_path(self, material_id: str) -> Path:
        return self.text_dir / f"{material_id}.txt"

    def resolve_course_folder(self, course: dict[str, Any]) -> Path:
        for key in ("folder_path", "source_path"):
            raw_path = str(course.get(key) or "").strip()
            if not raw_path:
                continue
            path = Path(raw_path).expanduser()
            if path.exists():
                return path.resolve()
            rebased = self.rebase_data_path(path)
            if rebased and rebased.exists():
                return rebased.resolve()
        fallback_name = Path(str(course.get("folder_path") or course.get("source_path") or course.get("name") or "course")).name
        return self.courses_dir / (fallback_name or slugify(str(course.get("name") or "course")))

    def resolve_material_path(self, material: dict[str, Any], course: dict[str, Any] | None = None) -> Path:
        raw_path = str(material.get("path") or "").strip()
        if raw_path:
            path = Path(raw_path).expanduser()
            if path.exists():
                return path.resolve()
            rebased = self.rebase_data_path(path)
            if rebased and rebased.exists():
                return rebased.resolve()
        relative_path = str(material.get("relative_path") or "").strip()
        if relative_path:
            owner = course or self.course_for_material(str(material.get("id") or ""))
            if owner:
                candidate = self.resolve_course_folder(owner) / relative_path
                if candidate.exists():
                    return candidate.resolve()
        return Path(raw_path).expanduser() if raw_path else self.data_dir / relative_path

    def rebase_data_path(self, path: Path) -> Path | None:
        parts = path.parts
        if "courses" in parts:
            index = len(parts) - 1 - list(reversed(parts)).index("courses")
            tail = parts[index + 1 :]
            if tail:
                return self.courses_dir.joinpath(*tail)
        if "previews" in parts:
            index = len(parts) - 1 - list(reversed(parts)).index("previews")
            tail = parts[index + 1 :]
            if tail:
                return (self.data_dir / "previews").joinpath(*tail)
        if "extracted-text" in parts:
            index = len(parts) - 1 - list(reversed(parts)).index("extracted-text")
            tail = parts[index + 1 :]
            if tail:
                return self.text_dir.joinpath(*tail)
        return None

    def normalize_state(self, state: dict[str, Any]) -> dict[str, Any]:
        state.setdefault("settings", {})
        state["settings"].setdefault("interface_language", "auto")
        state["settings"].setdefault("api_provider", os.getenv("CLW_ASSISTANT_PROVIDER", "local"))
        state["settings"].setdefault("api_model", os.getenv("CLW_ASSISTANT_MODEL", os.getenv("CLW_DEEPSEEK_MODEL", "deepseek-v4-flash")))
        state["settings"].setdefault("api_base_url", os.getenv("CLW_ASSISTANT_BASE_URL", os.getenv("CLW_DEEPSEEK_BASE_URL", "https://api.deepseek.com")))
        state["settings"].setdefault("storage_root", str(self.courses_dir))
        state.setdefault("courses", [])
        if state.get("course") and not state["courses"]:
            legacy_course = {
                **state["course"],
                "id": stable_id(state["course"].get("name", "course"), state["course"].get("source_path", "")),
                "folder_path": state["course"].get("source_path", str(self.courses_dir / slugify(state["course"].get("name", "course")))),
                "materials": state.get("materials", []),
                "notes": state.get("notes", []),
                "annotations": state.get("annotations", []),
                "units": [],
                "created_at": state.get("updated_at", utc_now()),
                "updated_at": state.get("updated_at", utc_now()),
            }
            state["courses"].append(legacy_course)
            state["active_course_id"] = legacy_course["id"]
        state.setdefault("active_course_id", state["courses"][0]["id"] if state["courses"] else None)
        for course in state["courses"]:
            course.setdefault("id", stable_id(course.get("name", "course"), course.get("folder_path", "")))
            course.setdefault("folder_path", course.get("source_path", str(self.courses_dir / slugify(course.get("name", "course")))))
            course.setdefault("source_path", course["folder_path"])
            course.setdefault("materials", [])
            course.setdefault("notes", [])
            course.setdefault("annotations", [])
            course.setdefault("units", [])
            course.setdefault("materials_seen", len(course["materials"]))
            course.setdefault("materials_parsed", sum(1 for item in course["materials"] if item.get("text_available")))
            course.setdefault("materials_failed", 0)
            for note in course["notes"]:
                note.setdefault("type", "reading_note")
                if self.is_assistant_generated_note(note):
                    note["type"] = "assistant_note"
            for annotation in course["annotations"]:
                annotation.setdefault("type", "annotation")
                annotation.setdefault("target_type", "text")
                annotation.setdefault("style", "comment")
                annotation.setdefault("body", annotation.get("comment", ""))
                annotation.setdefault("selected_text", "")
                annotation["rects"] = self.normalized_rects(annotation.get("rects", []))
                annotation["page"] = self.optional_positive_int(annotation.get("page"))
                annotation.setdefault("updated_at", annotation.get("created_at", utc_now()))
        active = self.active_course(state)
        state["course"] = self.course_summary(active) if active else None
        state["materials"] = active.get("materials", []) if active else []
        state["notes"] = active.get("notes", []) if active else []
        state["annotations"] = active.get("annotations", []) if active else []
        state.setdefault("updated_at", utc_now())
        return state

    def unique_course_folder(self, name: str) -> Path:
        base = self.courses_dir / slugify(name)
        candidate = base
        index = 2
        while candidate.exists():
            candidate = Path(f"{base}-{index}")
            index += 1
        return candidate

    def unique_unit_folder(self, course: dict[str, Any], name: str) -> str:
        base = slugify(name, fallback="unit")
        used = {item.get("folder_name") for item in course.get("units", [])}
        folder = base
        index = 2
        while folder in used or Path(course["folder_path"], folder).exists():
            folder = f"{base}-{index}"
            index += 1
        return folder

    @staticmethod
    def unique_file_path(path: Path) -> Path:
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        index = 2
        while True:
            candidate = path.with_name(f"{stem}-{index}{suffix}")
            if not candidate.exists():
                return candidate
            index += 1

    @staticmethod
    def optional_positive_int(value: Any) -> int | None:
        try:
            number = int(value)
        except (TypeError, ValueError):
            return None
        return number if number > 0 else None

    @staticmethod
    def normalized_rects(value: Any) -> list[dict[str, float]]:
        if not isinstance(value, list):
            return []
        rects: list[dict[str, float]] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            try:
                x = max(0.0, min(1.0, float(item.get("x", 0))))
                y = max(0.0, min(1.0, float(item.get("y", 0))))
                w = max(0.0, min(1.0 - x, float(item.get("w", 0))))
                h = max(0.0, min(1.0 - y, float(item.get("h", 0))))
            except (TypeError, ValueError):
                continue
            if w > 0.001 and h > 0.001:
                rects.append({"x": round(x, 6), "y": round(y, 6), "w": round(w, 6), "h": round(h, 6)})
        return rects

    @staticmethod
    def is_assistant_generated_note(note: dict[str, Any]) -> bool:
        body = str(note.get("body") or "").lstrip()
        return body.startswith("AI 学习辅助") or body.startswith("AI Study Assistant")

    @staticmethod
    def next_annotation_id(annotations: list[dict[str, Any]]) -> str:
        used = {item.get("id") for item in annotations}
        index = len(annotations) + 1
        while True:
            candidate = f"anno-{index:04d}"
            if candidate not in used:
                return candidate
            index += 1

    @staticmethod
    def course_by_id(state: dict[str, Any], course_id: str) -> dict[str, Any] | None:
        return next((course for course in state.get("courses", []) if course.get("id") == course_id), None)

    @classmethod
    def require_course(cls, state: dict[str, Any], course_id: str) -> dict[str, Any]:
        course = cls.course_by_id(state, course_id)
        if not course:
            raise ValueError("Course not found.")
        return course

    def active_course(self, state: dict[str, Any]) -> dict[str, Any] | None:
        course_id = state.get("active_course_id")
        return self.course_by_id(state, course_id) if course_id else None

    def course_for_material(self, material_id: str) -> dict[str, Any] | None:
        state = self.load()
        return next(
            (
                course
                for course in state.get("courses", [])
                if any(material.get("id") == material_id for material in course.get("materials", []))
            ),
            None,
        )

    @staticmethod
    def course_summary(course: dict[str, Any] | None) -> dict[str, Any] | None:
        if not course:
            return None
        return {
            "id": course["id"],
            "name": course["name"],
            "source_path": course.get("source_path"),
            "folder_path": course.get("folder_path"),
            "materials_seen": len(course.get("materials", [])),
            "materials_parsed": sum(1 for item in course.get("materials", []) if item.get("text_available")),
            "materials_failed": course.get("materials_failed", 0),
            "units": course.get("units", []),
            "created_at": course.get("created_at"),
            "updated_at": course.get("updated_at"),
        }

    def empty_state(self) -> dict[str, Any]:
        return self.normalize_state({"courses": [], "active_course_id": None, "settings": {}, "updated_at": utc_now()})
