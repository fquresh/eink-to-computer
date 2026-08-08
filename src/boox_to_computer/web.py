"""Tiny web UI: one button to process notes."""

from __future__ import annotations

import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template

from .config import Config
from .pipeline import process_inbox
from .state import load_state

TEMPLATE_DIR = Path(__file__).parent / "templates"


def create_app(config: Config) -> Flask:
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR))
    app.config["BOOX_CONFIG"] = config

    @app.route("/")
    def index():
        state = load_state(config.state_path)
        pending = [p for p in config.inbox.rglob("*.pdf") if not state.already_processed(_hash(p))]
        recent = sorted(
            state.processed.values(),
            key=lambda r: r.processed_at,
            reverse=True,
        )[:10]
        return render_template(
            "index.html",
            pending_count=len(pending),
            processed_count=len(state.processed),
            ocr_today=state.ocr_requests_today(),
            ocr_limit=config.gemini.requests_per_day,
            backend=config.backend,
            inbox=str(config.inbox),
            vault=str(config.vault),
            recent=recent,
        )

    @app.route("/process", methods=["POST"])
    def process():
        processed, failed = process_inbox(app.config["BOOX_CONFIG"])
        return jsonify({"processed": processed, "failed": failed})

    return app


def launch_gui(config: Config, port: int = 7788, open_browser: bool = True) -> None:
    app = create_app(config)
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(host="127.0.0.1", port=port, debug=False)


def _hash(path: Path) -> str:
    from .state import hash_file

    return hash_file(path)
