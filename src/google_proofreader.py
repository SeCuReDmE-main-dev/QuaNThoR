"""Compatibility shim for older imports.

The active proofreading helper now lives in :mod:`ollama_proofreader`.
"""

from __future__ import annotations

try:
    from .ollama_proofreader import GoogleProofreader, OllamaProofreader
except ImportError:  # pragma: no cover - allows direct script execution
    from ollama_proofreader import GoogleProofreader, OllamaProofreader

