"""Provider-neutral proofreading helper for school-safe QuaNThoR flows."""

from __future__ import annotations

from typing import Any, Dict, List


class SchoolProofreader:
    """Conservative local proofreading helper with no external AI dependency."""

    base_url = "local-heuristic"
    configured_model = "school-heuristic"
    model = "school-heuristic"

    def proofread_text(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return self._response("", provider="empty")
        return self._response(text, provider="school-heuristic")

    def _response(self, text: str, provider: str) -> Dict[str, Any]:
        improved = self._improve_text(text)
        return {
            "original_text": text,
            "improved_text": improved,
            "suggestions": self._generate_suggestions(text),
            "grammar_score": 0.85 if text else 1.0,
            "readability_score": 0.9 if text else 1.0,
            "provider": provider,
            "official_school_provider": True,
        }

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
