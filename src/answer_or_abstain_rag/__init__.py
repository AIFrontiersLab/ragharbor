"""Answer-or-Abstain RAG: governed reference service.

Detect insufficient evidence before generating an answer.

Public entry points:

* ``build_container`` - wire the full object graph from settings.
* ``run`` - execute a single request and return the outcome as a dict.
"""

from answer_or_abstain_rag.application.pipeline import run
from answer_or_abstain_rag.container import build_container
from answer_or_abstain_rag.version import __version__

__all__ = ["__version__", "build_container", "run"]
