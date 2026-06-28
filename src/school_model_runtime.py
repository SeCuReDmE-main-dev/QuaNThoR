"""Provider-neutral school model runtime helpers.

The official school route is provider-neutral. Legacy local model endpoints may
still be used by advanced users, but they are not official classroom providers.
"""

from __future__ import annotations

import os

try:
    from .ollama_runtime import extract_json_object, resolve_model, supports_structured_outputs
except ImportError:  # pragma: no cover - allows direct script execution
    from ollama_runtime import extract_json_object, resolve_model, supports_structured_outputs


def default_school_model_base_url() -> str:
    return os.getenv("SCHOOL_LLM_BASE_URL") or os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"


def school_model_auth_token() -> str | None:
    return (
        os.getenv("SCHOOL_LLM_API_KEY")
        or os.getenv("SCHOOL_LLM_AUTH_TOKEN")
        or os.getenv("OLLAMA_API_KEY")
        or os.getenv("OLLAMA_AUTH_TOKEN")
    )
