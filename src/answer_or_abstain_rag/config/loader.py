"""Load settings from defaults, an optional TOML profile, and environment overrides.

Precedence (lowest to highest): dataclass defaults < TOML file < environment.
Environment keys use a double underscore between section and field, e.g.
``ANSWER_OR_ABSTAIN_RAG_PIPELINE__TOP_K=5``.
"""

from __future__ import annotations

import dataclasses
import os
import tomllib
from pathlib import Path
from typing import Mapping

from answer_or_abstain_rag.config.schema import validate_settings
from answer_or_abstain_rag.config.settings import Settings
from answer_or_abstain_rag.kernel.errors import ConfigurationError

ENV_PREFIX = "ANSWER_OR_ABSTAIN_RAG_"


def load_settings(
    path: str | Path | None = None,
    *,
    env: Mapping[str, str] | None = None,
    overrides: dict | None = None,
) -> Settings:
    env = os.environ if env is None else env
    settings = Settings()
    config_path = path or env.get(f"{ENV_PREFIX}CONFIG")
    if config_path:
        file = Path(config_path)
        if not file.is_file():
            raise ConfigurationError(f"config file not found: {file}")
        with file.open("rb") as handle:
            _merge(settings, tomllib.load(handle), source=str(file))
    _merge(settings, _env_tree(env), source="environment")
    if overrides:
        _merge(settings, overrides, source="overrides")
    validate_settings(settings)
    return settings


def _env_tree(env: Mapping[str, str]) -> dict:
    tree: dict = {}
    for key, value in env.items():
        if not key.startswith(ENV_PREFIX) or key == f"{ENV_PREFIX}CONFIG":
            continue
        parts = key[len(ENV_PREFIX):].lower().split("__")
        if len(parts) != 2:
            continue
        tree.setdefault(parts[0], {})[parts[1]] = value
    return tree


def _merge(settings: Settings, data: dict, *, source: str) -> None:
    for section_name, values in (data or {}).items():
        section = getattr(settings, section_name, None)
        if section is None or not dataclasses.is_dataclass(section):
            raise ConfigurationError(f"unknown config section '{section_name}' in {source}")
        if not isinstance(values, dict):
            raise ConfigurationError(f"section '{section_name}' must be a table in {source}")
        known = {f.name: f for f in dataclasses.fields(section)}
        for key, raw in values.items():
            if key not in known:
                raise ConfigurationError(f"unknown key '{section_name}.{key}' in {source}")
            current = getattr(section, key)
            setattr(section, key, _coerce(raw, current, f"{section_name}.{key}"))


def _coerce(raw, current, name: str):
    if not isinstance(raw, str):
        return raw
    try:
        if isinstance(current, bool):
            lowered = raw.strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
            raise ValueError(raw)
        if isinstance(current, int):
            return int(raw)
        if isinstance(current, float):
            return float(raw)
        if isinstance(current, list):
            return [item.strip() for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise ConfigurationError(f"invalid value for {name}: {raw!r}") from exc
    return raw
