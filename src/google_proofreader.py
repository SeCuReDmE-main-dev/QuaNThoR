"""Compatibility shim for older imports.

The active school route now uses :mod:`school_proofreader`.
"""

from __future__ import annotations

try:
    from .school_proofreader import SchoolProofreader
except ImportError:  # pragma: no cover - allows direct script execution
    from school_proofreader import SchoolProofreader


GoogleProofreader = SchoolProofreader
OllamaProofreader = SchoolProofreader

