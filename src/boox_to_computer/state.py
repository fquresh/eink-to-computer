"""Content-hash based idempotency: never reprocess the same PDF."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class ProcessedRecord:
    note_path: str
    pages: int
    backend: str
    processed_at: str


@dataclass
class State:
    processed: dict[str, ProcessedRecord] = field(default_factory=dict)
    # Daily Gemini free-tier usage counter: {"2026-08-05": 12}
    ocr_usage: dict[str, int] = field(default_factory=dict)

    def already_processed(self, file_hash: str) -> bool:
        return file_hash in self.processed

    def mark_processed(self, file_hash: str, record: ProcessedRecord) -> None:
        self.processed[file_hash] = record

    def ocr_requests_today(self) -> int:
        return self.ocr_usage.get(_today(), 0)

    def record_ocr_requests(self, count: int) -> None:
        today = _today()
        self.ocr_usage[today] = self.ocr_usage.get(today, 0) + count
        # Keep only recent days so the file stays small.
        for day in sorted(self.ocr_usage)[:-7]:
            del self.ocr_usage[day]


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_state(path: Path) -> State:
    if not path.exists():
        return State()
    raw = json.loads(path.read_text())
    return State(
        processed={k: ProcessedRecord(**v) for k, v in raw.get("processed", {}).items()},
        ocr_usage=raw.get("ocr_usage", {}),
    )


def save_state(path: Path, state: State) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "processed": {k: asdict(v) for k, v in state.processed.items()},
        "ocr_usage": state.ocr_usage,
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(path)  # atomic
