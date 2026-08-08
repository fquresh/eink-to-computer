"""OCR backend protocol and the shared transcription prompt."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class TranscriptionError(Exception):
    """Raised when a page cannot be transcribed (caller should retry later)."""


TRANSCRIPTION_PROMPT = """\
Transcribe this handwritten page into clean Markdown.
Preserve headings, lists, and structure.
Convert diagrams or flowcharts to Mermaid code blocks where possible.
Use $...$ for math.
Mark anything you cannot read as [illegible].
Output only Markdown - no preamble, no code fences around the whole response.\
"""


class OCRBackend(Protocol):
    name: str

    def transcribe_page(self, image_path: Path) -> str:
        """Return Markdown transcription of one page image."""
        ...
