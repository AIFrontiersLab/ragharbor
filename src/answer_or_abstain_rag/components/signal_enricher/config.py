"""Static configuration for the Signal Enricher component."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SignalEnricherConfig:
    name: str = "signal_enricher"
    display_name: str = 'Signal Enricher'
    role: str = "enrich"
    interface: str = 'process(ctx) -> None'
    responsibility: str = 'Annotates candidates with token counts and query overlap, and collapses duplicate passages.'
    max_input_candidates: int = 10_000
    may_introduce_ids: bool = False
    enforce_sorted_output: bool = False


CONFIG = SignalEnricherConfig()
