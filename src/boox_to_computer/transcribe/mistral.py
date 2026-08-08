"""Mistral OCR backend (paid fallback)."""

from __future__ import annotations

import base64
import time
from pathlib import Path

import requests

from ..config import MistralConfig
from .base import TranscriptionError

OCR_ENDPOINT = "https://api.mistral.ai/v1/ocr"
MAX_ATTEMPTS = 4


class MistralBackend:
    name = "mistral"

    def __init__(self, config: MistralConfig) -> None:
        if not config.api_key:
            raise TranscriptionError(
                "Mistral API key missing. Set MISTRAL_API_KEY or mistral.api_key in config.yaml."
            )
        self._api_key = config.api_key
        self._model = config.model

    def transcribe_page(self, image_path: Path) -> str:
        encoded = base64.b64encode(image_path.read_bytes()).decode()
        payload = {
            "model": self._model,
            "document": {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{encoded}",
            },
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = requests.post(OCR_ENDPOINT, json=payload, headers=headers, timeout=120)
                if response.status_code == 429 or response.status_code >= 500:
                    raise requests.HTTPError(f"HTTP {response.status_code}", response=response)
                response.raise_for_status()
                pages = response.json().get("pages", [])
                text = "\n\n".join(p.get("markdown", "") for p in pages).strip()
                if not text:
                    raise TranscriptionError(f"Empty transcription for {image_path.name}")
                return text
            except TranscriptionError:
                raise
            except requests.RequestException as exc:
                if attempt == MAX_ATTEMPTS:
                    raise TranscriptionError(
                        f"Mistral OCR failed after {MAX_ATTEMPTS} attempts on {image_path.name}: {exc}"
                    ) from exc
                time.sleep(min(2**attempt * 5, 120))
        raise TranscriptionError("unreachable")
