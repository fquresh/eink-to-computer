from pathlib import Path

from boox_to_computer.state import (
    ProcessedRecord,
    State,
    hash_file,
    load_state,
    save_state,
)


def test_hash_file_stable(tmp_path: Path):
    f = tmp_path / "note.pdf"
    f.write_bytes(b"fake pdf")
    assert hash_file(f) == hash_file(f)


def test_state_roundtrip_and_idempotency(tmp_path: Path):
    path = tmp_path / "state.json"
    state = State()
    record = ProcessedRecord(
        note_path="/vault/note.md", pages=3, backend="gemini", processed_at="2026-08-05T10:00:00"
    )
    state.mark_processed("deadbeef", record)
    state.record_ocr_requests(3)
    save_state(path, state)

    loaded = load_state(path)
    assert loaded.already_processed("deadbeef")
    assert not loaded.already_processed("cafe")
    assert loaded.processed["deadbeef"].pages == 3
    assert loaded.ocr_requests_today() == 3


def test_load_state_missing_file(tmp_path: Path):
    state = load_state(tmp_path / "nope.json")
    assert state.processed == {}
    assert state.ocr_requests_today() == 0
