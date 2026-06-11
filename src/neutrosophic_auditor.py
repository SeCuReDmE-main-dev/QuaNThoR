"""Deterministic neutrosophic audit helpers for QuaNThoR workflows."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List


MIZAR_STRUCTURE_MARKERS = ("environ", "begin", "proof", "thus", "end;")
MATH_REQUEST_MARKERS = (
    "prove",
    "proof",
    "theorem",
    "lemma",
    "mizar",
    "formalize",
    "verify",
    "axiom",
    "definition",
)
PROSE_MARKERS = ("explain", "rewrite", "proofread", "grammar", "punctuation", "clarify")


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _contains_any(text: str, markers: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


class NeutrosophicAuditor:
    """Create a small T/I/F-style operational audit for routing decisions.

    The hierarchy is intentionally explicit:
    I -> I_system^S -> D_f -> dF -> i_fractal.

    The audit does not certify a theorem. It only reports operational evidence
    useful for deciding whether to draft, retrieve more context, verify, or ask
    for clarification.
    """

    def audit(
        self,
        text: str,
        *,
        context: str = "",
        route_decision: Dict[str, Any] | None = None,
        rag_context: str = "",
        rag_error: str | None = None,
        tool_result: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        clean_text = str(text or "").strip()
        clean_context = str(context or "").strip()
        route_decision = route_decision or {}
        tool_result = tool_result or {}

        notes: List[str] = []
        signals = self._collect_signals(clean_text, clean_context, route_decision, rag_context, rag_error, tool_result)

        if signals["has_mizar_code"]:
            notes.append("Input contains Mizar-like markers.")
        if signals["has_math_request"]:
            notes.append("Input contains mathematical drafting or verification intent.")
        if signals["has_prose_request"]:
            notes.append("Input contains prose/proofreading intent.")
        if rag_context:
            notes.append("RAG supplied context for the workflow.")
        if rag_error:
            notes.append("RAG was requested or inspected but was not available.")
        if signals["verification_success"]:
            notes.append("Mizar verifier returned success.")
        if signals["verification_failure"]:
            notes.append("Mizar verifier reported failure or parsed errors.")
        if signals["needs_clarification"]:
            notes.append("Router selected needs_clarification.")

        route_confidence = signals["route_confidence"]
        retrieval_support = 0.75 if rag_context else (0.2 if rag_error else 0.45)
        verification_support = 0.95 if signals["verification_success"] else (0.25 if signals["verification_failure"] else 0.5)

        T = _clamp((route_confidence * 0.4) + (retrieval_support * 0.25) + (verification_support * 0.35))
        I_system_S = _clamp(
            (0.35 if rag_error else 0.0)
            + (0.25 if not clean_context and not rag_context else 0.0)
            + (0.2 if route_confidence < 0.65 else 0.0)
            + (0.2 if signals["needs_clarification"] else 0.0)
        )
        D_f = _clamp(
            (0.35 if signals["route_conflict"] else 0.0)
            + (0.25 if signals["has_math_request"] and signals["has_prose_request"] else 0.0)
            + (0.2 if signals["has_mizar_code"] and signals["route"] == "draft_mizar" else 0.0)
        )
        dF = _clamp(
            (0.65 if signals["verification_failure"] else 0.0)
            + min(0.25, signals["error_count"] * 0.05)
        )
        F = _clamp(
            (0.45 if signals["needs_clarification"] else 0.0)
            + (0.35 if signals["verification_failure"] else 0.0)
            + (0.2 if rag_error and signals["route"] == "draft_mizar" else 0.0)
        )
        i_fractal = _clamp((I_system_S + D_f + dF) / 3)

        recommendation = self._recommend(T, I_system_S, D_f, dF, F, signals)

        return {
            "status": "success",
            "scores": {
                "T": T,
                "I_system_S": I_system_S,
                "D_f": D_f,
                "dF": dF,
                "F": F,
                "i_fractal": i_fractal,
            },
            "hierarchy": "I -> I_system^S -> D_f -> dF -> i_fractal",
            "recommendation": recommendation,
            "signals": signals,
            "notes": notes,
            "disclaimer": "Operational audit only; Mizar verification remains the mathematical authority.",
        }

    def _collect_signals(
        self,
        text: str,
        context: str,
        route_decision: Dict[str, Any],
        rag_context: str,
        rag_error: str | None,
        tool_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        route = str(route_decision.get("route") or "").strip().lower()
        route_confidence = _as_float(route_decision.get("confidence"), 0.5)
        errors = tool_result.get("errors") if isinstance(tool_result, dict) else []
        error_count = len(errors) if isinstance(errors, list) else 0
        tool_status = str(tool_result.get("status") or "").strip().lower() if isinstance(tool_result, dict) else ""

        lower_text = text.lower()
        structure_hits = sum(1 for marker in MIZAR_STRUCTURE_MARKERS if marker in lower_text)
        has_mizar_code = bool(
            re.search(r"\btheorem\s+\w+\s*:", text, re.I)
            or ("environ" in lower_text and "begin" in lower_text)
            or ("proof" in lower_text and "end;" in lower_text)
            or structure_hits >= 3
        )
        has_math_request = _contains_any(text, MATH_REQUEST_MARKERS)
        has_prose_request = _contains_any(text, PROSE_MARKERS)
        route_conflict = bool(
            (has_mizar_code and route not in {"verify_mizar", ""})
            or (has_prose_request and route == "verify_mizar")
            or (has_math_request and route == "proofread" and not has_prose_request)
        )

        return {
            "route": route or None,
            "route_confidence": _clamp(route_confidence),
            "input_length": len(text),
            "context_length": len(context),
            "rag_context_length": len(rag_context),
            "rag_error": rag_error,
            "has_mizar_code": has_mizar_code,
            "has_math_request": has_math_request,
            "has_prose_request": has_prose_request,
            "route_conflict": route_conflict,
            "needs_clarification": route == "needs_clarification",
            "verification_success": tool_status == "success" and error_count == 0,
            "verification_failure": tool_status == "failure" or error_count > 0,
            "error_count": error_count,
        }

    def _recommend(
        self,
        T: float,
        I_system_S: float,
        D_f: float,
        dF: float,
        F: float,
        signals: Dict[str, Any],
    ) -> str:
        if dF >= 0.5:
            return "inspect_mizar_errors"
        if signals["needs_clarification"] or I_system_S >= 0.55 or D_f >= 0.45:
            return "ask_clarifying_question"
        if F >= 0.55:
            return "avoid_using_current_context"
        if T >= 0.7 and signals["route"] == "draft_mizar":
            return "draft_then_verify"
        if T >= 0.7 and signals["route"] == "verify_mizar":
            return "verify_now"
        return "proceed_carefully"
