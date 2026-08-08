from datetime import datetime
from pathlib import Path

from boox_to_computer.emit import build_markdown, emit_note, slugify


def test_slugify():
    assert slugify("Product brainstorm!") == "product-brainstorm"
    assert slugify("  Q3 Planning (draft) ") == "q3-planning-draft"
    assert slugify("!!!") == "untitled"


def test_build_markdown_structure():
    md = build_markdown(
        title="Product brainstorm",
        notebook="Work",
        pdf_hash="abc123",
        page_images=["product-brainstorm-p1.png"],
        transcriptions=["- idea one\n- idea two"],
        created=datetime(2026, 8, 5, 10, 30),
    )
    assert md.startswith("---\n")
    assert 'title: "Product brainstorm"' in md
    assert "created: 2026-08-05" in md
    assert "tags:\n  - boox\n  - handwritten" in md
    assert "boox_pdf_hash: abc123" in md
    assert "![[attachments/product-brainstorm-p1.png]]" in md
    assert "- idea one" in md


def test_emit_note_writes_note_and_attachments(tmp_path: Path):
    notes_dir = tmp_path / "vault" / "Handwritten Boox Notes"
    image = tmp_path / "page-001.png"
    image.write_bytes(b"png-bytes")

    note_path = emit_note(
        notes_dir=notes_dir,
        notebook="Work",
        title="Product brainstorm",
        pdf_hash="abc123",
        page_image_paths=[image],
        transcriptions=["hello world"],
        created=datetime(2026, 8, 5),
    )

    assert note_path == notes_dir / "Work" / "product-brainstorm.md"
    assert note_path.exists()
    attachment = notes_dir / "Work" / "attachments" / "product-brainstorm-p1.png"
    assert attachment.read_bytes() == b"png-bytes"
    assert "hello world" in note_path.read_text()
