"""Draft conservative Mizar articles from natural-language requests."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

import requests

try:
    from .school_model_runtime import (
        default_school_model_base_url,
        extract_json_object,
        resolve_model,
        school_model_auth_token,
        supports_structured_outputs,
    )
except ImportError:  # pragma: no cover - allows direct script execution
    from school_model_runtime import (
        default_school_model_base_url,
        extract_json_object,
        resolve_model,
        school_model_auth_token,
        supports_structured_outputs,
    )


class MizarDraftAssistant:
    """Turn user requests into cautious Mizar drafts and follow-up questions."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 75,
    ) -> None:
        configured_base = (
            base_url
            or os.getenv("SCHOOL_LLM_MIZAR_BASE_URL")
            or os.getenv("SCHOOL_LLM_BASE_URL")
            or os.getenv("OLLAMA_MIZAR_BASE_URL")
            or os.getenv("OLLAMA_BASE_URL")
        )
        self.base_url = self._normalize_base_url(configured_base or default_school_model_base_url())
        self.configured_model = (
            model
            or os.getenv("SCHOOL_LLM_DRAFT_MODEL")
            or os.getenv("SCHOOL_LLM_MIZAR_MODEL")
            or os.getenv("SCHOOL_LLM_MODEL")
            or os.getenv("OLLAMA_DRAFT_MODEL")
            or os.getenv("OLLAMA_MIZAR_MODEL")
            or os.getenv("OLLAMA_MODEL")
            or "qwen2.5:7b"
        )
        self.model = resolve_model(
            self.base_url,
            self.configured_model,
            fallback_models=(
                "gpt-oss:120b-cloud",
                "qwen2.5:7b",
                "qwen2-math:7b",
                "phi4-mini-reasoning",
                "mistral",
                "llama3.1",
            ),
            auth_token=school_model_auth_token(),
        )
        self.timeout_seconds = timeout_seconds
        self.auth_token = school_model_auth_token()

    def draft_from_query(self, query: str, context: str | None = None) -> Dict[str, Any]:
        if not query or not query.strip():
            return self._heuristic_response("", context or "", provider="empty")

        try:
            payload = self._build_payload(query, context)
            response = requests.post(
                self._endpoint("chat"),
                json=payload,
                headers=self._headers(),
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return self._parse_model_response(query, context or "", response.json())
        except Exception as exc:  # noqa: BLE001 - deliberate fallback path
            return self._heuristic_response(query, context or "", provider="heuristic", error=str(exc))

    def _build_payload(self, query: str, context: str | None) -> Dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "normalized_query": {"type": "string"},
                "mizar_draft": {"type": "string"},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "clarifying_questions": {"type": "array", "items": {"type": "string"}},
                "editing_suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "original": {"type": "string"},
                            "suggested": {"type": "string"},
                            "explanation": {"type": "string"},
                        },
                        "required": ["type", "original", "suggested", "explanation"],
                    },
                },
                "proof_strategy": {"type": "string"},
                "confidence": {"type": "number"},
                "ready_for_verifier": {"type": "boolean"},
            },
            "required": [
                "status",
                "normalized_query",
                "mizar_draft",
                "assumptions",
                "clarifying_questions",
                "editing_suggestions",
                "proof_strategy",
                "confidence",
                "ready_for_verifier",
            ],
        }

        prompt = (
            "Convert the user request into a conservative Mizar draft.\n"
            "Rules:\n"
            "- Use standard Mizar structure with environ, begin, theorem, proof, end.\n"
            "- Do not invent theorems, vocabularies, or lemmas.\n"
            "- If the request is ambiguous, keep the draft partial and ask clarifying questions.\n"
            "- Improve punctuation and readability of the user request.\n"
            "- Return only JSON matching the schema.\n\n"
            f"User request:\n{query}\n\n"
            f"Context:\n{context or 'none'}"
        )

        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a careful formal-math drafting assistant for Mizar. "
                        "Prefer a useful skeleton over a false proof."
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

    def _parse_model_response(
        self,
        query: str,
        context: str,
        response_json: Dict[str, Any],
    ) -> Dict[str, Any]:
        content = response_json.get("message", {}).get("content")
        if content is None:
            content = response_json.get("response")
        parsed = extract_json_object(content)

        clarifying_questions = self._coerce_string_list(parsed.get("clarifying_questions"))
        status = self._normalize_status(parsed.get("status"), clarifying_questions)

        return {
            "status": status,
            "original_query": query,
            "context": context,
            "normalized_query": self._coerce_text(parsed.get("normalized_query"), self._normalize_query_text(query)),
            "mizar_draft": self._coerce_text(parsed.get("mizar_draft"), self._heuristic_draft(query, context)),
            "assumptions": self._coerce_string_list(
                parsed.get("assumptions"),
                default=self._default_assumptions(query, context),
            ),
            "clarifying_questions": clarifying_questions,
            "editing_suggestions": self._coerce_suggestions(parsed.get("editing_suggestions", []), query),
            "proof_strategy": self._coerce_text(parsed.get("proof_strategy"), self._default_strategy(query)),
            "confidence": self._coerce_score(parsed.get("confidence"), 0.55),
            "ready_for_verifier": bool(parsed.get("ready_for_verifier", False)),
            "provider": "school-model-runtime",
        }

    def _heuristic_response(
        self,
        query: str,
        context: str,
        provider: str,
        error: str | None = None,
    ) -> Dict[str, Any]:
        normalized_query = self._normalize_query_text(query)
        assumptions = self._default_assumptions(query, context)
        clarifying_questions = self._default_questions(query)
        return {
            "status": self._normalize_status(None, clarifying_questions),
            "original_query": query,
            "context": context,
            "normalized_query": normalized_query,
            "mizar_draft": self._heuristic_draft(query, context),
            "assumptions": assumptions,
            "clarifying_questions": clarifying_questions,
            "editing_suggestions": self._generate_suggestions(query),
            "proof_strategy": self._default_strategy(query),
            "confidence": 0.45 if query else 0.2,
            "ready_for_verifier": False,
            "provider": provider,
            "error": error,
        }

    def _normalize_status(self, raw_status: Any, clarifying_questions: List[str]) -> str:
        normalized = str(raw_status or "").strip().lower()
        if normalized in {"draft", "needs_more_context"}:
            return normalized
        return "needs_more_context" if clarifying_questions else "draft"

    def _heuristic_draft(self, query: str, context: str) -> str:
        normalized = self._normalize_query_text(query) or "Formalize the request"
        context_block = f"\n:: Context: {context}" if context else ""
        return (
            "environ\n\n"
            "begin\n\n"
            f":: User request: {normalized}{context_block}\n"
            ":: TODO: replace this skeleton with a precise theorem statement.\n"
            "theorem\n"
            "  :: statement goes here\n"
            "proof\n"
            "  :: proof steps go here\n"
            "end;\n\n"
            "end."
        )

    def _default_assumptions(self, query: str, context: str) -> List[str]:
        assumptions = ["The formal statement may need additional mathematical context."]
        if context.strip():
            assumptions.append("The supplied context should be treated as a draft constraint, not as a verified lemma.")
        if query.strip():
            assumptions.append("The natural-language request is the source of intent for the formal draft.")
        return assumptions

    def _default_questions(self, query: str) -> List[str]:
        cleaned = query.lower()
        questions: List[str] = []

        if any(token in cleaned for token in ("prove", "show", "demonstrate")):
            questions.append("What exact theorem statement should be proved?")
        if any(token in cleaned for token in ("even", "odd", "prime", "continuous", "finite", "infinite")):
            questions.append("Which domain and assumptions should be fixed for the variables?")
        if "for all" not in cleaned and "exists" not in cleaned and "there exists" not in cleaned:
            questions.append("Should the final statement be universal, existential, or conditional?")

        return questions[:3]

    def _default_strategy(self, query: str) -> str:
        if not query.strip():
            return "Start with a precise theorem statement, then refine the hypothesis list."
        return (
            "Translate the user intent into a theorem statement, list the assumptions explicitly, "
            "then use standard Mizar structure and fill the proof only after the statement is fixed."
        )

    def _generate_suggestions(self, query: str) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []
        normalized = self._normalize_query_text(query)

        if query and query != normalized:
            suggestions.append(
                {
                    "type": "style",
                    "original": query,
                    "suggested": normalized,
                    "explanation": "Clean the wording before formalization so the theorem intent is unambiguous.",
                }
            )

        if query and not query.endswith((".", "?", "!")):
            suggestions.append(
                {
                    "type": "punctuation",
                    "original": query,
                    "suggested": f"{query}.",
                    "explanation": "Add a terminal punctuation mark to make the request easier to parse.",
                }
            )

        return suggestions

    def _normalize_query_text(self, query: str) -> str:
        cleaned = re.sub(r"\s+", " ", query).strip()
        if not cleaned:
            return cleaned
        cleaned = cleaned[0].upper() + cleaned[1:]
        if cleaned[-1] not in ".?!":
            cleaned += "."
        return cleaned

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

    def _coerce_suggestions(self, suggestions: Any, original_text: str) -> List[Dict[str, Any]]:
        if not isinstance(suggestions, list):
            return self._generate_suggestions(original_text)

        cleaned: List[Dict[str, Any]] = []
        for suggestion in suggestions:
            if not isinstance(suggestion, dict):
                continue
            cleaned.append(
                {
                    "type": str(suggestion.get("type", "style")),
                    "original": str(suggestion.get("original", original_text)),
                    "suggested": str(suggestion.get("suggested", original_text)),
                    "explanation": str(suggestion.get("explanation", "Improvement suggested by school model runtime.")),
                }
            )
        return cleaned or self._generate_suggestions(original_text)
