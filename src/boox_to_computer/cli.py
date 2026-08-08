"""boox-to-computer CLI: watch | process <pdf> | status"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .ingest import watch
from .pipeline import process_inbox, process_pdf
from .state import load_state
from .web import launch_gui


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="boox-to-computer",
        description="Boox handwritten note PDFs -> vision OCR -> Obsidian markdown",
    )
    parser.add_argument(
        "--config", type=Path, default=None, help="Path to config.yaml (default: ./config.yaml)"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("watch", help="Watch the inbox and process PDFs as they arrive")
    commands.add_parser("sync", help="Process all pending PDFs in the inbox, then exit")
    gui_cmd = commands.add_parser("gui", help="Launch the web UI (one-button processor)")
    gui_cmd.add_argument("--port", type=int, default=7788, help="Port for the web UI (default: 7788)")
    gui_cmd.add_argument("--no-browser", action="store_true", help="Don't auto-open the browser")
    process_cmd = commands.add_parser("process", help="Process a single PDF")
    process_cmd.add_argument("pdf", type=Path)
    commands.add_parser("status", help="Show processed notes and OCR usage")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.command == "watch":
        watch(config)
        return 0
    if args.command == "gui":
        launch_gui(config, port=args.port, open_browser=not args.no_browser)
        return 0
    if args.command == "sync":
        processed, failed = process_inbox(config)
        print(f"done: {processed} processed, {failed} failed")
        return 1 if failed else 0
    if args.command == "process":
        if not args.pdf.exists():
            print(f"error: no such file: {args.pdf}", file=sys.stderr)
            return 2
        note = process_pdf(args.pdf, config)
        return 0 if note else 1
    if args.command == "status":
        state = load_state(config.state_path)
        print(f"processed notes: {len(state.processed)}")
        print(f"OCR requests today: {state.ocr_requests_today()} / {config.gemini.requests_per_day}")
        for record in state.processed.values():
            print(f"  {record.processed_at}  {record.note_path}  ({record.pages}p, {record.backend})")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
