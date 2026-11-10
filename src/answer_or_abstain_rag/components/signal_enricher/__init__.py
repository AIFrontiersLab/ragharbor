"""Signal Enricher.

Annotates candidates with token counts and query overlap, and collapses duplicate passages.
"""

from answer_or_abstain_rag.components.signal_enricher.adapter import ROLE, build
from answer_or_abstain_rag.components.signal_enricher.config import CONFIG, SignalEnricherConfig
from answer_or_abstain_rag.components.signal_enricher.errors import SignalEnricherError
from answer_or_abstain_rag.components.signal_enricher.service import SignalEnricherService

__all__ = ["CONFIG", "ROLE", "build", "SignalEnricherConfig", "SignalEnricherError", "SignalEnricherService"]
