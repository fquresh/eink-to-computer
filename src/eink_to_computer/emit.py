"""Write Obsidian-ready markdown notes with page image attachments."""

from __future__ import annotations

import re
import shutil
from datetime import datetime
from pathlib import Path

ATTACHMENTS_DIR = "attachments"


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()
    return slug or "untitled"


def build_markdown(
    title: str,
    notebook: str,
    pdf_hash: str,
    page_images: list[str],
    transcriptions: list[str],
    created: datetime,
) -> str:
    frontmatter = "\n".join(
        [
            "---",
            f"title: {_yaml_string(title)}",
            f"created: {created.date().isoformat()}",
            "source: eink",
            f"notebook: {_yaml_string(notebook)}",
            "tags:",
            "  - eink",
            "  - handwritten",
            f"boox_pdf_hash: {pdf_hash}",
            "---",
            "",
        ]
    )
    parts = [frontmatter, f"# {title}\n"]
    for page_number, (image_name, text) in enumerate(zip(page_images, transcriptions), start=1):
        parts.append(f"## Page {page_number}\n")
        parts.append(f"![[{ATTACHMENTS_DIR}/{image_name}]]\n")
        parts.append(text + "\n")
    return "\n".join(parts)


def emit_note(
    notes_dir: Path,
    notebook: str,
    title: str,
    pdf_hash: str,
    page_image_paths: list[Path],
    transcriptions: list[str],
    created: datetime,
) -> Path:
    """Write the note and its attachments into the vault. Returns the note path."""
    slug = slugify(title)
    note_dir = notes_dir / notebook if notebook else notes_dir
    attachments_dir = note_dir / ATTACHMENTS_DIR
    attachments_dir.mkdir(parents=True, exist_ok=True)

    image_names: list[str] = []
    for index, image_path in enumerate(page_image_paths, start=1):
        image_name = f"{slug}-p{index}.png"
        shutil.copyfile(image_path, attachments_dir / image_name)
        image_names.append(image_name)

    markdown = build_markdown(title, notebook, pdf_hash, image_names, transcriptions, created)
    note_path = note_dir / f"{slug}.md"
    _write_atomic(note_path, markdown)
    return note_path


def _write_atomic(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    tmp.replace(path)


def _yaml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
