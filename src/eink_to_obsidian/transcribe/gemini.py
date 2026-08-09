"""Gemini vision OCR backend with free-tier rate limiting."""

from __future__ import annotations

import time
from pathlib import Path

from google import genai

from ..config import GeminiConfig
from ..state import State
from .base import TRANSCRIPTION_PROMPT, TranscriptionError

MAX_ATTEMPTS = 4


class GeminiBackend:
    name = "gemini"

    def __init__(self, config: GeminiConfig, state: State) -> None:
        if not config.api_key:
            raise TranscriptionError(
                "Gemini API key missing. Set GEMINI_API_KEY or gemini.api_key in config.yaml."
            )
        self._client = genai.Client(api_key=config.api_key)
        self._model = config.model
        self._min_interval = 60.0 / config.requests_per_minute
        self._daily_limit = config.requests_per_day
        self._state = state
        self._last_request_at = 0.0

    def transcribe_page(self, image_path: Path) -> str:
        self._enforce_rate_limits(image_path)
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                uploaded = self._client.files.upload(file=image_path)
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=[TRANSCRIPTION_PROMPT, uploaded],
                )
                self._state.record_ocr_requests(1)
                text = (response.text or "").strip()
                if not text:
                    raise TranscriptionError(f"Empty transcription for {image_path.name}")
                return text
            except TranscriptionError:
                raise
            except Exception as exc:  # network errors, 429s, 5xx from the SDK
                if attempt == MAX_ATTEMPTS:
                    raise TranscriptionError(
                        f"Gemini failed after {MAX_ATTEMPTS} attempts on {image_path.name}: {exc}"
                    ) from exc
                time.sleep(min(2**attempt * 5, 120))
        raise TranscriptionError("unreachable")

    def _enforce_rate_limits(self, image_path: Path) -> None:
        if self._state.ocr_requests_today() >= self._daily_limit:
            raise TranscriptionError(
                f"Gemini free-tier daily limit ({self._daily_limit}) reached; "
                f"re-run tomorrow or switch backend. Skipping {image_path.name}."
            )
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_at = time.monotonic()
