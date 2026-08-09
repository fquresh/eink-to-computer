"""Fully local OCR backend via Ollama (e.g. qwen3-vl)."""

from __future__ import annotations

import base64
from pathlib import Path

import requests

from ..config import LocalConfig
from .base import TRANSCRIPTION_PROMPT, TranscriptionError


class LocalBackend:
    name = "local"

    def __init__(self, config: LocalConfig) -> None:
        self._endpoint = f"{config.host.rstrip('/')}/api/generate"
        self._model = config.model

    def transcribe_page(self, image_path: Path) -> str:
        payload = {
            "model": self._model,
            "prompt": TRANSCRIPTION_PROMPT,
            "images": [base64.b64encode(image_path.read_bytes()).decode()],
            "stream": False,
        }
        try:
            response = requests.post(self._endpoint, json=payload, timeout=600)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise TranscriptionError(
                f"Local OCR failed on {image_path.name} (is Ollama running?): {exc}"
            ) from exc
        text = response.json().get("response", "").strip()
        if not text:
            raise TranscriptionError(f"Empty transcription for {image_path.name}")
        return text
