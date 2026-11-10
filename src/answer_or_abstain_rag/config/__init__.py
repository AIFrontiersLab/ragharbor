"""Typed configuration: defaults in code, profiles in TOML, overrides from the environment."""

from answer_or_abstain_rag.config.loader import load_settings
from answer_or_abstain_rag.config.settings import Settings

__all__ = ["Settings", "load_settings"]
