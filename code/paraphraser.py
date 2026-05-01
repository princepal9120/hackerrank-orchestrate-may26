"""Optional controlled paraphrasing hook.

Deterministic answer generation always happens first. By default this module does
nothing, which keeps the submitted agent reproducible and dependency-free. A future
provider-backed paraphraser can only be added here after routing and validation.
"""
from __future__ import annotations

import os


def paraphrase_if_enabled(response: str, evidence: str) -> str:
    if os.getenv("ENABLE_LLM_PARAPHRASE", "0") != "1":
        return response
    _ = evidence
    return response
