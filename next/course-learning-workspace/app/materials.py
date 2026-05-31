from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree


SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt", ".csv", ".docx", ".pptx", ".xlsx", ".pdf"}
IGNORED_DIRS = {
    ".academic-os",
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".pytest_cache",
    ".ruff_cache",
}
GENERATED_OUTPUT_DIRS = {("notes", "open-academic-os")}
MAX_MATERIAL_BYTES = 50 * 1024 * 1024


@dataclass(frozen=True)
class ParsedBlock:
    text: str
    locator: str = "text"
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ParseResult:
    title: str
    kind: str
    blocks: list[ParsedBlock]
    status: str = "ok"
    diagnostics: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n\n".join(block.text for block in self.blocks if block.text.strip())


def scan_folder(source_path: str | Path) -> tuple[dict, list[dict], dict[str, str]]:
    root = Path(source_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Course materials folder must exist: {root}")

    files = [path for path in root.rglob("*") if is_supported_material(root, path)]
    materials: list[dict] = []
    extracted_texts: dict[str, str] = {}
    parsed = 0
    failed = 0

    for path in sorted(files):
        result = parse_file(path)
        relative_path = str(path.relative_to(root))
        material_id = stable_id(str(root), relative_path, path.stat().st_size, path.stat().st_mtime_ns)
        text = result.text.strip()
        if result.status in {"ok", "empty"}:
            parsed += 1
        else:
            failed += 1
        if text:
            extracted_texts[material_id] = text
        materials.append(
            {
                "id": material_id,
                "title": result.title,
                "kind": result.kind,
                "status": result.status,
                "relative_path": relative_path,
                "path": str(path),
                "bytes": path.stat().st_size,
                "diagnostics": result.diagnostics,
                "text_available": bool(text),
                "text_preview": text[:480],
                "locators": [block.locator for block in result.blocks[:12] if block.text.strip()],
            }
        )

    course = {
        "name": root.name or "Course",
        "source_path": str(root),
        "materials_seen": len(files),
        "materials_parsed": parsed,
        "materials_failed": failed,
    }
    return course, materials, extracted_texts


def is_supported_material(root: Path, path: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    try:
        relative_parts = path.resolve().relative_to(root.resolve()).parts
    except ValueError:
        return False
    if any(part in IGNORED_DIRS for part in relative_parts):
        return False
    if is_generated_relative_path(relative_parts):
        return False
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False
    try:
        return path.stat().st_size <= MAX_MATERIAL_BYTES
    except OSError:
        return False


def parse_file(path: Path) -> ParseResult:
    suffix = path.suffix.lower()
    title = normalize_title(path.stem) or path.name
    try:
        if suffix in {".md", ".markdown", ".txt", ".csv"}:
            return parse_plain_text(path, title, suffix.lstrip("."))
        if suffix == ".docx":
            return parse_docx(path, title)
        if suffix == ".pptx":
            return parse_pptx(path, title)
        if suffix == ".xlsx":
            return parse_xlsx(path, title)
        if suffix == ".pdf":
            return parse_pdf(path, title)
    except Exception as exc:  # pragma: no cover - diagnostic path
        return ParseResult(title=title, kind=suffix.lstrip(".") or "file", blocks=[], status="failed", diagnostics=[str(exc)])
    return ParseResult(title=title, kind="unsupported", blocks=[], status="unsupported", diagnostics=[f"Unsupported extension: {suffix}"])


def parse_plain_text(path: Path, title: str, kind: str) -> ParseResult:
    text = normalize_text(path.read_text(encoding="utf-8", errors="ignore"))
    return ParseResult(title=title, kind=kind, blocks=[ParsedBlock(text=text)], status="ok" if text else "empty")


def parse_docx(path: Path, title: str) -> ParseResult:
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.startswith("word/document")]
        blocks = [ParsedBlock(text=text, locator="document") for name in names if (text := xml_text(archive.read(name)))]
    return ParseResult(title=title, kind="docx", blocks=blocks, status="ok" if blocks else "empty")


def parse_pptx(path: Path, title: str) -> ParseResult:
    with zipfile.ZipFile(path) as archive:
        slide_names = sorted(
            [name for name in archive.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)],
            key=lambda name: int(re.search(r"slide(\d+)\.xml", name).group(1)),  # type: ignore[union-attr]
        )
        blocks = []
        for index, name in enumerate(slide_names, start=1):
            text = xml_text(archive.read(name))
            if text:
                blocks.append(ParsedBlock(text=text, locator=f"slide {index}", metadata={"slide": str(index)}))
    return ParseResult(title=title, kind="pptx", blocks=blocks, status="ok" if blocks else "empty")


def parse_xlsx(path: Path, title: str) -> ParseResult:
    with zipfile.ZipFile(path) as archive:
        shared_strings = xlsx_shared_strings(archive)
        sheet_names = sorted(
            [name for name in archive.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", name)],
            key=lambda name: int(re.search(r"sheet(\d+)\.xml", name).group(1)),  # type: ignore[union-attr]
        )
        blocks = []
        for index, name in enumerate(sheet_names, start=1):
            text = xlsx_sheet_text(archive.read(name), shared_strings)
            if text:
                blocks.append(ParsedBlock(text=text, locator=f"sheet {index}", metadata={"sheet": str(index)}))
    return ParseResult(title=title, kind="xlsx", blocks=blocks, status="ok" if blocks else "empty")


def parse_pdf(path: Path, title: str) -> ParseResult:
    diagnostics: list[str] = []
    if shutil.which("pdftotext"):
        try:
            completed = subprocess.run(
                ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            text = normalize_text(completed.stdout)
            if text:
                return ParseResult(title=title, kind="pdf", blocks=[ParsedBlock(text=text, locator="pdf text")])
            if completed.stderr.strip():
                diagnostics.append(f"pdftotext failed: {completed.stderr.strip()[:240]}")
        except Exception as exc:  # pragma: no cover - depends on local PDF tools
            diagnostics.append(f"pdftotext failed: {exc}")

    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        blocks = []
        for index, page in enumerate(reader.pages, start=1):
            text = normalize_text(page.extract_text() or "")
            if text:
                blocks.append(ParsedBlock(text=text, locator=f"page {index}", metadata={"page": str(index)}))
        return ParseResult(title=title, kind="pdf", blocks=blocks, status="ok" if blocks else "empty")
    except ImportError:
        diagnostics.append("Optional dependency `pypdf` is not installed; used basic PDF fallback.")
    except Exception as exc:  # pragma: no cover - depends on external PDFs
        diagnostics.append(f"pypdf failed: {exc}")

    diagnostics.append("PDF text extraction failed; the file may be scanned, encrypted, damaged, or unsupported.")
    return ParseResult(title=title, kind="pdf", blocks=[], status="needs_parser", diagnostics=diagnostics)


def xml_text(xml_bytes: bytes) -> str:
    root = ElementTree.fromstring(xml_bytes)
    pieces: list[str] = []
    for node in root.iter():
        if node.tag.endswith("}t") and node.text:
            pieces.append(node.text)
        elif node.tag.endswith("}tab"):
            pieces.append("\t")
        elif node.tag.endswith("}br"):
            pieces.append("\n")
    return normalize_text(" ".join(pieces))


def xlsx_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in root:
        pieces = [node.text for node in item.iter() if node.tag.endswith("}t") and node.text]
        strings.append(normalize_text(" ".join(pieces)))
    return strings


def xlsx_sheet_text(xml_bytes: bytes, shared_strings: list[str]) -> str:
    root = ElementTree.fromstring(xml_bytes)
    rows: list[str] = []
    for row in root.iter():
        if not row.tag.endswith("}row"):
            continue
        cells: list[str] = []
        for cell in row:
            if not cell.tag.endswith("}c"):
                continue
            value = xlsx_cell_text(cell, shared_strings)
            if value:
                cells.append(value)
        if cells:
            rows.append("\t".join(cells))
    return normalize_text("\n".join(rows))


def xlsx_cell_text(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        pieces = [node.text for node in cell.iter() if node.tag.endswith("}t") and node.text]
        return normalize_text(" ".join(pieces))
    value_node = next((node for node in cell if node.tag.endswith("}v")), None)
    if value_node is None or value_node.text is None:
        return ""
    raw = value_node.text
    if cell_type == "s":
        try:
            return shared_strings[int(raw)]
        except (ValueError, IndexError):
            return ""
    return normalize_text(raw)


def rank_materials(question: str, materials: list[dict], texts: dict[str, str], material_id: str | None = None) -> list[dict]:
    terms = set(tokenize(question))
    if not terms:
        return []
    candidates = [item for item in materials if not material_id or item["id"] == material_id]
    ranked: list[dict] = []
    for material in candidates:
        text = texts.get(material["id"], "")
        if not text:
            continue
        best_quote = ""
        best_score = 0
        for chunk in chunk_text(text):
            score = len(terms.intersection(tokenize(chunk)))
            if score > best_score:
                best_score = score
                best_quote = chunk
        if best_score:
            ranked.append({**material, "score": best_score, "quote": best_quote[:640]})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)[:5]


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    paragraphs = [item.strip() for item in re.split(r"\n{2,}", text) if item.strip()]
    chunks: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue
        for start in range(0, len(paragraph), max_chars):
            chunks.append(paragraph[start : start + max_chars])
    return chunks


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for token in re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]+", text):
        token = token.lower()
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            if len(token) == 2:
                tokens.append(token)
            elif len(token) > 2:
                tokens.extend(token[index : index + 2] for index in range(len(token) - 1))
            continue
        if len(token) > 1:
            tokens.append(token)
    return tokens


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def normalize_title(value: str) -> str:
    value = value.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", value).strip()


def stable_id(*parts: object, length: int = 24) -> str:
    digest = hashlib.sha256("::".join(str(part) for part in parts).encode("utf-8")).hexdigest()
    return digest[:length]


def is_generated_relative_path(parts: tuple[str, ...]) -> bool:
    return any(parts[index : index + len(prefix)] == prefix for prefix in GENERATED_OUTPUT_DIRS for index in range(len(parts)))
