"""Ollama-backed proofreading helper with heuristic fallback."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import requests

try:
    from .ollama_runtime import default_ollama_base_url, extract_json_object, resolve_model, supports_structured_outputs
except ImportError:  # pragma: no cover - allows direct script execution
    from ollama_runtime import default_ollama_base_url, extract_json_object, resolve_model, supports_structured_outputs


class OllamaProofreader:
    """Use a remote Ollama endpoint when available, otherwise fall back locally."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 45,
    ) -> None:
        configured_base = base_url or os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST")
        self.base_url = self._normalize_base_url(configured_base or default_ollama_base_url())
        self.configured_model = (
            model
            or os.getenv("OLLAMA_PROOFREADER_MODEL")
            or os.getenv("OLLAMA_MODEL")
            or "qwen2.5:7b"
        )
        self.model = resolve_model(
            self.base_url,
            self.configured_model,
            fallback_models=(
                "gpt-oss:120b-cloud",
                "qwen2.5:7b",
                "qwen2.5:3b",
                "mistral",
                "llama3.1",
            ),
            auth_token=os.getenv("OLLAMA_API_KEY") or os.getenv("OLLAMA_AUTH_TOKEN"),
        )
        self.timeout_seconds = timeout_seconds
        self.auth_token = os.getenv("OLLAMA_API_KEY") or os.getenv("OLLAMA_AUTH_TOKEN")

    def proofread_text(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return self._heuristic_response("", provider="empty")

        try:
            payload = self._build_payload(text)
            response = requests.post(
                self._endpoint("chat"),
                json=payload,
                headers=self._headers(),
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return self._parse_ollama_response(text, response.json())
        except Exception as exc:  # noqa: BLE001 - fallback path is deliberate
            return self._heuristic_response(text, provider="heuristic", error=str(exc))

    def _build_payload(self, text: str) -> Dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {
                "improved_text": {"type": "string"},
                "suggestions": {
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
                "grammar_score": {"type": "number"},
                "readability_score": {"type": "number"},
            },
            "required": ["improved_text", "suggestions", "grammar_score", "readability_score"],
        }

        prompt = (
            "Rewrite the following explanation so it is clearer for students and mathematicians. "
            "Return only valid JSON that matches the provided schema.\n\n"
            f"Text:\n{text}"
        )
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a careful writing assistant for mathematical education. Keep meaning intact.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        if supports_structured_outputs(self.model):
            payload["format"] = schema
        else:
            payload["messages"][1]["content"] += "\n\nJSON schema:\n" + json.dumps(schema, indent=2)
        return payload

    def _parse_ollama_response(self, original_text: str, response_json: Dict[str, Any]) -> Dict[str, Any]:
        content = response_json.get("message", {}).get("content")
        if content is None:
            content = response_json.get("response")
        parsed = extract_json_object(content)

        return {
            "original_text": original_text,
            "improved_text": self._coerce_text(parsed.get("improved_text"), original_text),
            "suggestions": self._coerce_suggestions(parsed.get("suggestions", []), original_text),
            "grammar_score": self._coerce_score(parsed.get("grammar_score"), 0.85),
            "readability_score": self._coerce_score(parsed.get("readability_score"), 0.9),
            "provider": "ollama",
        }

    def _heuristic_response(self, text: str, provider: str, error: str | None = None) -> Dict[str, Any]:
        improved = self._improve_text(text)
        return {
            "original_text": text,
            "improved_text": improved,
            "suggestions": self._generate_suggestions(text),
            "grammar_score": 0.85 if text else 1.0,
            "readability_score": 0.9 if text else 1.0,
            "provider": provider,
            "error": error,
        }

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

    def _coerce_suggestions(self, suggestions: Any, original_text: str) -> List[Dict[str, Any]]:
        if not isinstance(suggestions, list):
            return self._generate_suggestions(original_text)

        cleaned: List[Dict[str, Any]] = []
        for suggestion in suggestions:
            if not isinstance(suggestion, dict):
                continue
            cleaned.append(
                {
                    "type": str(suggestion.get("type", "grammar")),
                    "original": str(suggestion.get("original", original_text)),
                    "suggested": str(suggestion.get("suggested", original_text)),
                    "explanation": str(suggestion.get("explanation", "Improvement suggested by Ollama.")),
                }
            )
        return cleaned or self._generate_suggestions(original_text)

    def _improve_text(self, text: str) -> str:
        improvements = {
            "cant": "can't",
            "dont": "don't",
            "wont": "won't",
            "its ": "it's ",
            " i ": " I ",
        }

        improved = text
        for old, new in improvements.items():
            improved = improved.replace(old, new)
        return improved

    def _generate_suggestions(self, text: str) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []

        if "cant" in text:
            suggestions.append(
                {
                    "type": "grammar",
                    "original": "cant",
                    "suggested": "can't",
                    "explanation": "Add an apostrophe for the contraction.",
                }
            )

        if text and text.count(".") == 0 and len(text) > 10:
            suggestions.append(
                {
                    "type": "punctuation",
                    "original": text,
                    "suggested": f"{text}.",
                    "explanation": "Consider ending the sentence with a period.",
                }
            )

        return suggestions


GoogleProofreader = OllamaProofreader
