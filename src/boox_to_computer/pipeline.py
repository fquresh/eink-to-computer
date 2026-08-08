"""Orchestration: PDF in inbox -> rendered pages -> OCR -> Obsidian note."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

from .config import Config
from .emit import emit_note
from .render import render_pdf_pages
from .state import ProcessedRecord, State, hash_file, load_state, save_state
from .transcribe import OCRBackend, TranscriptionError, build_backend


def process_pdf(
    pdf_path: Path,
    config: Config,
    state: State | None = None,
    backend: OCRBackend | None = None,
) -> Path | None:
    """Process one exported note PDF. Returns the note path, or None if skipped."""
    state = state if state is not None else load_state(config.state_path)
    file_hash = hash_file(pdf_path)
    if state.already_processed(file_hash):
        print(f"skip (already processed): {pdf_path.name}")
        return None

    if backend is None:
        backend = build_backend(config, state)

    notebook = _notebook_name(pdf_path, config.inbox)
    title = pdf_path.stem

    with tempfile.TemporaryDirectory() as tmp:
        page_images = render_pdf_pages(pdf_path, Path(tmp))
        transcriptions = [
            backend.transcribe_page(image) for image in page_images
        ]
        note_path = emit_note(
            notes_dir=config.notes_dir,
            notebook=notebook,
            title=title,
            pdf_hash=file_hash,
            page_image_paths=page_images,
            transcriptions=transcriptions,
            created=datetime.fromtimestamp(pdf_path.stat().st_mtime),
        )

    state.mark_processed(
        file_hash,
        ProcessedRecord(
            note_path=str(note_path),
            pages=len(page_images),
            backend=backend.name,
            processed_at=datetime.now().isoformat(timespec="seconds"),
        ),
    )
    save_state(config.state_path, state)
    print(f"processed: {pdf_path.name} -> {note_path}")
    return note_path


def process_inbox(config: Config) -> tuple[int, int]:
    """Process every pending PDF in the inbox. Returns (processed, failed) counts."""
    state = load_state(config.state_path)
    backend: OCRBackend | None = None
    processed = failed = 0
    for pdf_path in sorted(config.inbox.rglob("*.pdf")):
        try:
            if backend is None:
                backend = build_backend(config, state)
            if process_pdf(pdf_path, config, state=state, backend=backend) is not None:
                processed += 1
        except TranscriptionError as exc:
            failed += 1
            print(f"failed (will retry next run): {pdf_path.name}: {exc}")
        except Exception as exc:
            failed += 1
            print(f"error: {pdf_path.name}: {exc}")
    return processed, failed


def _notebook_name(pdf_path: Path, inbox: Path) -> str:
    """Mirror the inbox subfolder structure as the notebook name."""
    parent = pdf_path.parent
    if parent == inbox:
        return ""
    return parent.relative_to(inbox).parts[0]
