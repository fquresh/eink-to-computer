"""OpenRouter vision backend (OpenAI-compatible chat completions API)."""

from __future__ import annotations

import base64
import time
from pathlib import Path

import requests

from ..config import OpenRouterConfig
from .base import TRANSCRIPTION_PROMPT, TranscriptionError

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MAX_ATTEMPTS = 4


class OpenRouterBackend:
    name = "openrouter"

    def __init__(self, config: OpenRouterConfig) -> None:
        if not config.api_key:
            raise TranscriptionError(
                "OpenRouter API key missing. Set OPENROUTER_API_KEY or openrouter.api_key in config.yaml."
            )
        self._api_key = config.api_key
        self._model = config.model
        self._base_url = config.base_url

    def transcribe_page(self, image_path: Path) -> str:
        encoded = base64.b64encode(image_path.read_bytes()).decode()
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": TRANSCRIPTION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded}",
                            },
                        },
                    ],
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }
        url = f"{self._base_url.rstrip('/')}/chat/completions"
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=120)
                if response.status_code == 429 or response.status_code >= 500:
                    raise requests.HTTPError(
                        f"HTTP {response.status_code}", response=response
                    )
                response.raise_for_status()
                data = response.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                text = text.strip()
                if not text:
                    raise TranscriptionError(f"Empty transcription for {image_path.name}")
                return text
            except TranscriptionError:
                raise
            except requests.RequestException as exc:
                if attempt == MAX_ATTEMPTS:
                    raise TranscriptionError(
                        f"OpenRouter failed after {MAX_ATTEMPTS} attempts on {image_path.name}: {exc}"
                    ) from exc
                time.sleep(min(2**attempt * 5, 120))
        raise TranscriptionError("unreachable")
