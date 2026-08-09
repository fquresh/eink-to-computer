"""Pluggable OCR backends."""

from __future__ import annotations

from ..config import Config
from ..state import State
from .base import OCRBackend, TranscriptionError

__all__ = ["OCRBackend", "TranscriptionError", "build_backend"]


def build_backend(config: Config, state: State) -> OCRBackend:
    if config.backend == "gemini":
        from .gemini import GeminiBackend

        return GeminiBackend(config.gemini, state)
    if config.backend == "mistral":
        from .mistral import MistralBackend

        return MistralBackend(config.mistral)
    if config.backend == "local":
        from .local import LocalBackend

        return LocalBackend(config.local)
    if config.backend == "openrouter":
        from .openrouter import OpenRouterBackend

        return OpenRouterBackend(config.openrouter)
    raise ValueError(f"Unknown OCR backend: {config.backend!r}")
