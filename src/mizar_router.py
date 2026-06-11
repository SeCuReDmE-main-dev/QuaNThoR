"""Route QuaNThoR requests to proofreading, drafting, or verification."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

import requests

try:
    from .ollama_runtime import default_ollama_base_url, extract_json_object, resolve_model, supports_structured_outputs
except ImportError:  # pragma: no cover - allows direct script execution
    from ollama_runtime import default_ollama_base_url, extract_json_object, resolve_model, supports_structured_outputs


VALID_ROUTES = {"proofread", "draft_mizar", "verify_mizar", "needs_clarification"}


class MizarWorkflowRouter:
    """Classify incoming text before the server executes a QuaNThoR tool."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        configured_base = base_url or os.getenv("OLLAMA_ROUTER_BASE_URL") or os.getenv("OLLAMA_BASE_URL")
        self.base_url = self._normalize_base_url(configured_base or default_ollama_base_url())
        self.configured_model = (
            model
            or os.getenv("OLLAMA_ROUTER_MODEL")
            or os.getenv("OLLAMA_MIZAR_MODEL")
            or os.getenv("OLLAMA_MODEL")
            or "qwen2.5:7b"
        )
        self.model = resolve_model(
            self.base_url,
            self.configured_model,
            fallback_models=(
                "mizar-specialist",
                "gpt-oss:120b-cloud",
                "qwen2.5:7b",
                "qwen2-math:7b",
                "mistral",
                "llama3.1",
            ),
            auth_token=os.getenv("OLLAMA_API_KEY") or os.getenv("OLLAMA_AUTH_TOKEN"),
        )
        self.timeout_seconds = timeout_seconds
        self.auth_token = os.getenv("OLLAMA_API_KEY") or os.getenv("OLLAMA_AUTH_TOKEN")

    def route(self, text: str, context: str | None = None) -> Dict[str, Any]:
        cleaned = str(text or "").strip()
        if not cleaned:
            return self._heuristic_route(cleaned, context or "", error="empty_input")

        try:
            payload = self._build_payload(cleaned, context or "")
            response = requests.post(
                self._endpoint("chat"),
                json=payload,
                headers=self._headers(),
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return self._parse_ollama_response(cleaned, context or "", response.json())
        except Exception as exc:  # noqa: BLE001 - fallback classification keeps the app usable
            return self._heuristic_route(cleaned, context or "", error=str(exc))

    def _build_payload(self, text: str, context: str) -> Dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {
                "route": {"type": "string", "enum": sorted(VALID_ROUTES)},
                "confidence": {"type": "number"},
                "reason": {"type": "string"},
                "normalized_text": {"type": "string"},
                "clarifying_questions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["route", "confidence", "reason", "normalized_text", "clarifying_questions"],
        }

        prompt = (
            "Classify the user input for QuaNThoR.\n"
            "Available routes:\n"
            "- proofread: polish prose, explanations, or verifier feedback.\n"
            "- draft_mizar: convert a natural-language theorem/proof request into a Mizar draft.\n"
            "- verify_mizar: verify a complete or near-complete Mizar article.\n"
            "- needs_clarification: ask questions because the math or intent is too ambiguous.\n\n"
            "Return only JSON matching the schema. Do not execute any tool.\n\n"
            f"Input:\n{text}\n\nContext:\n{context or 'none'}"
        )
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a routing controller for a Mizar verification service. "
                        "Keep route selection conservative and never claim verification."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        if supports_structured_outputs(self.model):
            payload["format"] = schema
        else:
            payload["messages"][1]["content"] += "\n\nJSON schema:\n" + json.dumps(schema, indent=2)
        return payload

    def _parse_ollama_response(self, text: str, context: str, response_json: Dict[str, Any]) -> Dict[str, Any]:
        content = response_json.get("message", {}).get("content")
        if content is None:
            content = response_json.get("response")
        parsed = extract_json_object(content)
        fallback = self._heuristic_route(text, context)

        route = str(parsed.get("route") or fallback["route"]).strip().lower()
        if route not in VALID_ROUTES:
            route = fallback["route"]
        use_fallback_fields = False
        if route == "needs_clarification" and fallback["route"] == "proofread":
            route = "proofread"
            use_fallback_fields = True

        return {
            "route": route,
            "confidence": fallback["confidence"]
            if use_fallback_fields
            else self._coerce_score(parsed.get("confidence"), fallback["confidence"]),
            "reason": fallback["reason"] if use_fallback_fields else self._coerce_text(parsed.get("reason"), fallback["reason"]),
            "normalized_text": self._coerce_text(parsed.get("normalized_text"), fallback["normalized_text"]),
            "clarifying_questions": self._coerce_string_list(
                [] if use_fallback_fields else parsed.get("clarifying_questions"),
                fallback["clarifying_questions"],
            ),
            "provider": "ollama",
            "model": self.model,
        }

    def _heuristic_route(self, text: str, context: str, error: str | None = None) -> Dict[str, Any]:
        normalized = self._normalize_text(text)
        lowered = normalized.lower()
        questions: List[str] = []

        if not normalized:
            route = "needs_clarification"
            reason = "No input was provided."
            questions = ["What text, theorem request, or Mizar article should QuaNThoR process?"]
            confidence = 0.95
        elif self._looks_like_mizar_article(normalized):
            route = "verify_mizar"
            reason = "The input looks like a Mizar article."
            confidence = 0.88
        elif self._looks_like_feedback_prose(lowered):
            route = "proofread"
            reason = "The input looks like prose feedback rather than a request for formalization."
            confidence = 0.86
        elif self._looks_like_formalization_request(lowered):
            questions = self._clarifying_questions(lowered)
            route = "needs_clarification" if questions else "draft_mizar"
            reason = "The input asks for a mathematical statement to be formalized in Mizar."
            confidence = 0.72 if questions else 0.82
        else:
            route = "proofread"
            reason = "The input looks like prose or explanatory text."
            confidence = 0.7

        result = {
            "route": route,
            "confidence": confidence,
            "reason": reason,
            "normalized_text": normalized,
            "clarifying_questions": questions,
            "provider": "heuristic",
            "model": self.model,
        }
        if error:
            result["error"] = error
        return result

    def _looks_like_mizar_article(self, text: str) -> bool:
        lowered = text.lower()
        has_article_shape = "begin" in lowered and ("theorem" in lowered or "definition" in lowered)
        has_proof_shape = "proof" in lowered and re.search(r"\bend\s*;", lowered)
        return ("environ" in lowered and has_article_shape) or (has_article_shape and has_proof_shape)

    def _looks_like_formalization_request(self, lowered: str) -> bool:
        triggers = (
            "mizar",
            "formalize",
            "formalise",
            "prove",
            "proof",
            "theorem",
            "lemma",
            "draft",
            "translate",
            "tradu",
            "prouve",
            "demontr",
            "démontr",
            "théorème",
            "theoreme",
        )
        return any(trigger in lowered for trigger in triggers)

    def _looks_like_feedback_prose(self, lowered: str) -> bool:
        feedback_markers = (
            "verified successfully",
            "verification failed",
            "the proof verified",
            "the proof has been",
            "mizar reported",
            "error at line",
            "accepted by mizar",
        )
        return any(marker in lowered for marker in feedback_markers)

    def _clarifying_questions(self, lowered: str) -> List[str]:
        ambiguous_terms = ("sequence", "function", "set", "space", "group", "ring", "converges", "continuous")
        if not any(term in lowered for term in ambiguous_terms):
            return []
        return [
            "What exact theorem statement should be formalized?",
            "Which domain, assumptions, and variable types should be fixed?",
        ]

    def _endpoint(self, path: str) -> str:
        base = self.base_url.rstrip("/")
        if base.endswith("/api"):
            return f"{base}/{path}"
        return f"{base}/api/{path}"

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def _normalize_base_url(self, base_url: str) -> str:
        base = base_url.strip()
        if not base.startswith(("http://", "https://")):
            base = f"http://{base}"
        return base.rstrip("/")

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"[ \t]+", " ", str(text or "").strip())

    def _coerce_text(self, value: Any, fallback: str) -> str:
        return value if isinstance(value, str) and value.strip() else fallback

    def _coerce_score(self, value: Any, fallback: float) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError):
            score = fallback
        return max(0.0, min(1.0, score))

    def _coerce_string_list(self, value: Any, default: List[str] | None = None) -> List[str]:
        default = default or []
        if not isinstance(value, list):
            return list(default)
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        return cleaned or list(default)
