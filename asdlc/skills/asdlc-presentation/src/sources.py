"""Discover slides and ordered narration; validate SVG inputs and metadata."""
import re
from pathlib import Path
from defusedxml import ElementTree as ET
from contracts import PresentationError, SlideSource

FOLDER = re.compile(r"^(\d{2,})-[a-z0-9]+(?:-[a-z0-9]+)*$")
NOTES = {"speaker-text.md", "speaker-notes.md", "speaker-notes-01-intro.md"}
SUPPLEMENTS = ("speaker-notes-02-walkthrough.md", "speaker-notes-03-details.md")
PROFILES = {"intro", "detailed"}
VISUAL = {".svg", ".puml", ".mmd", ".plantuml", ".mermaid"}
SVG_NS = "http://www.w3.org/2000/svg"
MAX_SOURCE_BYTES = 20 * 1024 * 1024


def safe_svg(path: Path) -> bool:
    """Allow self-contained SVG; reject external resources and active content."""
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise PresentationError(f"SVG exceeds 20 MiB: {path}")
    raw = path.read_bytes()
    try:
        root = ET.fromstring(raw)
    except Exception as exc:
        raise PresentationError(f"Invalid or unsafe SVG: {path}: {exc}") from exc
    if root.tag != f"{{{SVG_NS}}}svg":
        raise PresentationError(f"Not a namespaced SVG document: {path}")
    raster = False
    for el in root.iter():
        local = el.tag.rsplit("}", 1)[-1]
        if local.lower() in {"script", "foreignobject", "iframe", "include"}:
            raise PresentationError(f"Active/external SVG element {local}: {path}")
        for key, value in el.attrib.items():
            key = key.rsplit("}", 1)[-1].lower()
            if key.startswith("on") or key == "base":
                raise PresentationError(f"Active SVG attribute {key}: {path}")
            if key in {"href", "src"} and not value.startswith("#"):
                if el.tag == f"{{{SVG_NS}}}image" and re.fullmatch(
                    r"data:image/(png|jpeg);base64,[A-Za-z0-9+/=\s]+", value
                ):
                    raster = True
                else:
                    raise PresentationError(f"External/unsupported SVG reference: {path}")
        # Reject CSS escapes/imports to keep URL validation unambiguous.
        style = el.text or "" if local == "style" else ""
        style += " " + el.attrib.get("style", "")
        if "@" in style or "\\" in style:
            raise PresentationError(f"Unsupported CSS import/escape: {path}")
        for value in [style, *el.attrib.values()]:
            for match in re.finditer(r"url\s*\((.*?)\)", value, re.I | re.S):
                target = match.group(1).strip().strip("\"'")
                if not target.startswith("#"):
                    raise PresentationError(f"External CSS resource: {path}")
    return raster


def read_notes(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8-sig")
    references = []
    def metadata(match):
        references.append(match.group(1).strip())
        return ""
    text = re.sub(r"<!--(.*?)-->", metadata, text, flags=re.S)
    title = path.parent.name
    lines = []
    metadata_section = False
    for line in text.splitlines():
        if line.startswith(("AI-MODIFIED - ", "PME-APPROVED - ")):
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if re.match(r"^##\s+(Fine print|Sources|References)\s*$", line, re.I):
            metadata_section = True
        if metadata_section:
            references.append(line)
        else:
            lines.append(line)
    narration = "\n".join(lines).strip()
    if not narration:
        raise PresentationError(f"Empty narration: {path}")
    return title, narration, "\n".join(references).strip()


def discover(presentation: Path, profile: str = "intro") -> list[SlideSource]:
    if profile not in PROFILES:
        raise PresentationError(f"Unknown narration profile: {profile}")
    presentation = presentation.resolve(strict=True)
    if not presentation.is_dir():
        raise PresentationError(f"Not a presentation directory: {presentation}")
    children = [p for p in presentation.iterdir() if p.is_dir() and p.name != "build"]
    invalid = [p.name for p in children if p.is_symlink() or not FOLDER.fullmatch(p.name)]
    if invalid:
        raise PresentationError(f"Unnumbered/invalid slide directories: {invalid}")
    folders = sorted(children, key=lambda p: int(p.name.split("-", 1)[0]))
    numbers = [int(p.name.split("-", 1)[0]) for p in folders]
    if numbers != list(range(1, len(folders) + 1)) or not folders:
        raise PresentationError(f"Slide numbers must be contiguous from 01: {numbers}")
    result = []
    for number, folder in zip(numbers, folders):
        entries = [p for p in folder.iterdir() if p.name != ".DS_Store"]
        visuals = [p for p in entries if p.suffix.lower() in VISUAL]
        notes = [p for p in entries if p.name in NOTES]
        extra = [p for name in SUPPLEMENTS for p in entries if p.name == name]
        if len(visuals) != 1 or len(notes) != 1 or len(entries) != 2 + len(extra):
            raise PresentationError(f"Expected one visual, one intro, and optional ordered notes: {folder}")
        if extra and extra[0].name != SUPPLEMENTS[0]:
            raise PresentationError(f"Detailed notes require a walkthrough first: {folder}")
        if profile == "detailed" and not extra:
            raise PresentationError(f"Detailed profile requires a walkthrough for every slide: {folder}")
        if any(p.is_symlink() or not p.is_file() for p in entries):
            raise PresentationError(f"Source files must be regular local files: {folder}")
        if visuals[0].suffix.lower() != ".svg":
            raise PresentationError("Builder v0.2 renders SVG only; PlantUML/Mermaid adapters are pending")
        raster = safe_svg(visuals[0])
        # Validate every supplied part; select the profile explicitly, never guess.
        parts = [notes[0], *extra]
        parsed = [read_notes(p) for p in parts]
        chosen = parts if profile == "detailed" else parts[:1]
        selected = parsed if profile == "detailed" else parsed[:1]
        title = parsed[0][0]
        narration = "\n\n".join(part[1] for part in selected)
        references = "\n\n".join(part[2] for part in selected if part[2])
        result.append(SlideSource(number, folder, visuals[0], notes[0], title,
                                  narration, references, raster, tuple(chosen)))
    return result
