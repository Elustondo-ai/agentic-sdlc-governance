"""Public build contracts. Inputs are immutable source artifacts, not a PPTX."""
from dataclasses import dataclass
from pathlib import Path


class PresentationError(ValueError):
    """A source, validation, or output-boundary requirement was not satisfied."""


@dataclass(frozen=True)
class SlideSource:
    number: int
    folder: Path
    visual: Path
    notes: Path
    title: str
    narration: str
    references: str
    raster_backed: bool
    note_files: tuple[Path, ...] = ()


@dataclass(frozen=True)
class BuildResult:
    presentation: Path
    pptx: Path
    manifest: Path
    slide_count: int
    warnings: tuple[str, ...]
