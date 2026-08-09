"""Configuration loading for eink-to-computer."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATHS = [
    Path("config.yaml"),
    Path.home() / ".config" / "eink-to-computer" / "config.yaml",
]


@dataclass
class GeminiConfig:
    api_key: str = ""
    model: str = "gemini-3.5-flash"
    requests_per_minute: int = 10
    requests_per_day: int = 250


@dataclass
class MistralConfig:
    api_key: str = ""
    model: str = "mistral-ocr-latest"


@dataclass
class LocalConfig:
    host: str = "http://127.0.0.1:11434"
    model: str = "qwen3-vl"


@dataclass
class OpenRouterConfig:
    api_key: str = ""
    model: str = "qwen/qwen3-vl-32b-instruct"
    base_url: str = "https://openrouter.ai/api/v1"


@dataclass
class Config:
    inbox: Path
    vault: Path
    notes_folder: str = "Handwritten Notes"
    backend: str = "gemini"
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    mistral: MistralConfig = field(default_factory=MistralConfig)
    local: LocalConfig = field(default_factory=LocalConfig)
    openrouter: OpenRouterConfig = field(default_factory=OpenRouterConfig)

    @property
    def notes_dir(self) -> Path:
        return self.vault / self.notes_folder

    @property
    def state_path(self) -> Path:
        return self.inbox / ".eink-to-computer-state.json"


def _resolve_api_key(config_value: str, env_var: str) -> str:
    return os.environ.get(env_var) or config_value


def load_config(path: Path | None = None) -> Config:
    if path is None:
        for candidate in DEFAULT_CONFIG_PATHS:
            if candidate.exists():
                path = candidate
                break
        else:
            raise FileNotFoundError(
                "No config.yaml found. Copy config.example.yaml to config.yaml and fill it in."
            )
    raw = yaml.safe_load(path.read_text()) or {}

    cfg = Config(
        inbox=Path(raw.get("inbox", "~/boox-inbox")).expanduser(),
        vault=Path(raw["vault"]).expanduser(),
        notes_folder=raw.get("notes_folder", "Handwritten Boox Notes"),
        backend=raw.get("backend", "gemini"),
        gemini=GeminiConfig(**raw.get("gemini", {})),
        mistral=MistralConfig(**raw.get("mistral", {})),
        local=LocalConfig(**raw.get("local", {})),
        openrouter=OpenRouterConfig(**raw.get("openrouter", {})),
    )
    cfg.gemini.api_key = _resolve_api_key(cfg.gemini.api_key, "GEMINI_API_KEY")
    cfg.mistral.api_key = _resolve_api_key(cfg.mistral.api_key, "MISTRAL_API_KEY")
    cfg.openrouter.api_key = _resolve_api_key(cfg.openrouter.api_key, "OPENROUTER_API_KEY")
    return cfg
