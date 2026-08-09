"""Watch the inbox folder and process PDFs as they arrive."""

from __future__ import annotations

import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import Config
from .pipeline import process_pdf

SETTLE_SECONDS = 3.0  # let the file finish copying before reading it


class _PdfHandler(FileSystemEventHandler):
    def __init__(self, config: Config) -> None:
        self._config = config

    def on_created(self, event) -> None:
        self._maybe_process(event)

    def on_modified(self, event) -> None:
        self._maybe_process(event)

    def _maybe_process(self, event) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".pdf":
            return
        time.sleep(SETTLE_SECONDS)
        try:
            process_pdf(path, self._config)
        except Exception as exc:
            print(f"error processing {path.name}: {exc} (will retry on next watch restart)")


def watch(config: Config) -> None:
    config.inbox.mkdir(parents=True, exist_ok=True)
    config.notes_dir.mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(_PdfHandler(config), str(config.inbox), recursive=True)
    observer.start()
    print(f"watching {config.inbox} -> {config.notes_dir}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
