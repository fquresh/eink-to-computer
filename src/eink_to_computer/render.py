"""Render PDF pages to PNG images suitable for vision OCR."""

from __future__ import annotations

from pathlib import Path

import pymupdf

RENDER_DPI = 200


def render_pdf_pages(pdf_path: Path, out_dir: Path, dpi: int = RENDER_DPI) -> list[Path]:
    """Render each page of a PDF to a PNG. Returns ordered page image paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    page_images: list[Path] = []
    with pymupdf.open(pdf_path) as doc:
        zoom = dpi / 72.0
        matrix = pymupdf.Matrix(zoom, zoom)
        for index, page in enumerate(doc, start=1):
            image_path = out_dir / f"page-{index:03d}.png"
            page.get_pixmap(matrix=matrix).save(image_path)
            page_images.append(image_path)
    return page_images
