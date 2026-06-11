"""Pure-Python plithogenic quaternion audit helpers for retrieval traces."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


MIZAR_MARKERS = (
    "environ",
    "begin",
    "proof",
    "theorem",
    "definition",
    "lemma",
    "end;",
    "xboole",
    "tarski",
    "pre_topc",
    "subset",
)


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text or "") if len(token) > 2}


@dataclass(frozen=True)
class Quaternion:
    """Quaternion with Hamilton product operations.

    The auditor uses q=(T, I_system_S, D_f, dF). F is not stored inside the
    quaternion; it remains an external damping coefficient.
    """

    w: float
    x: float
    y: float
    z: float

    @classmethod
    def identity(cls) -> "Quaternion":
        return cls(1.0, 0.0, 0.0, 0.0)

    def norm(self) -> float:
        return math.sqrt((self.w * self.w) + (self.x * self.x) + (self.y * self.y) + (self.z * self.z))

    def normalize(self, fallback: "Quaternion | None" = None) -> "Quaternion":
        length = self.norm()
        if length <= 1e-12:
            return fallback or Quaternion.identity()
        return Quaternion(
            round(self.w / length, 6),
            round(self.x / length, 6),
            round(self.y / length, 6),
            round(self.z / length, 6),
        )

    def conjugate(self) -> "Quaternion":
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def hamilton(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(
            (self.w * other.w) - (self.x * other.x) - (self.y * other.y) - (self.z * other.z),
            (self.w * other.x) + (self.x * other.w) + (self.y * other.z) - (self.z * other.y),
            (self.w * other.y) - (self.x * other.z) + (self.y * other.w) + (self.z * other.x),
            (self.w * other.z) + (self.x * other.y) - (self.y * other.x) + (self.z * other.w),
        )

    def rotate(self, vector: "Quaternion") -> "Quaternion":
        unit = self.normalize()
        return unit.hamilton(vector).hamilton(unit.conjugate()).normalize(vector)

    def damp(self, coefficient: float) -> "Quaternion":
        coefficient = _clamp(coefficient)
        return Quaternion(self.w * coefficient, self.x * coefficient, self.y * coefficient, self.z * coefficient)

    def to_dict(self) -> Dict[str, float]:
        return {
            "T": round(self.w, 6),
            "I_system_S": round(self.x, 6),
            "D_f": round(self.y, 6),
            "dF": round(self.z, 6),
        }


@dataclass(frozen=True)
class PlithogenicAttribute:
    name: str
    value: float
    dominant_value: float
    contradiction_degree: float
    weight: float

    def effective_weight(self) -> float:
        return _clamp(self.weight * (1.0 - self.contradiction_degree))

    def weighted_value(self) -> float:
        return _clamp(self.value * self.effective_weight())

    def to_dict(self) -> Dict[str, float | str]:
        return {
            "name": self.name,
            "value": _clamp(self.value),
            "dominant_value": _clamp(self.dominant_value),
            "contradiction_degree": _clamp(self.contradiction_degree),
            "weight": _clamp(self.weight),
            "effective_weight": self.effective_weight(),
            "weighted_value": self.weighted_value(),
        }


@dataclass(frozen=True)
class RetrievalRelationState:
    query: str
    evidence_id: str
    relation_quaternion: Quaternion
    falsity_damping: float
    attributes: List[PlithogenicAttribute] = field(default_factory=list)
    source_metadata: Dict[str, Any] = field(default_factory=dict)

    def weighted_quaternion(self) -> Quaternion:
        if not self.attributes:
            support = self.falsity_damping
        else:
            support = sum(attribute.effective_weight() for attribute in self.attributes) / len(self.attributes)
            support *= self.falsity_damping
        return self.relation_quaternion.damp(support).normalize(self.relation_quaternion)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "evidence_id": self.evidence_id,
            "relation_quaternion": self.relation_quaternion.to_dict(),
            "weighted_quaternion": self.weighted_quaternion().to_dict(),
            "falsity_damping": _clamp(self.falsity_damping),
            "attributes": [attribute.to_dict() for attribute in self.attributes],
            "source_metadata": self.source_metadata,
        }


class PlithogenicQuaternionAuditor:
    """Build a classical, zero-dependency relation audit over retrieval output."""

    def audit(
        self,
        text: str,
        *,
        context: str = "",
        retrieval: Any = None,
        neutrosophic_audit: Dict[str, Any] | None = None,
        tool_result: Dict[str, Any] | None = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        clean_text = str(text or "").strip()
        clean_context = str(context or "").strip()
        tool_result = tool_result or {}
        scores = dict((neutrosophic_audit or {}).get("scores") or {})

        T = _clamp(_as_float(scores.get("T"), 0.45))
        I_system_S = _clamp(_as_float(scores.get("I_system_S"), 0.2))
        D_f = _clamp(_as_float(scores.get("D_f"), 0.2))
        dF = _clamp(_as_float(scores.get("dF"), 0.0))
        F = _clamp(_as_float(scores.get("F"), 0.0))
        i_fractal = _clamp(_as_float(scores.get("i_fractal"), (I_system_S + D_f + dF) / 3))

        base_quaternion = Quaternion(T, I_system_S, D_f, dF).normalize()
        evidence_items = self._extract_evidence(retrieval, clean_context, top_k)
        if not evidence_items:
            evidence_items = [{"id": "input", "text": clean_text, "metadata": {"source": "input_only"}}]

        relation_states = [
            self._build_relation_state(clean_text, item, base_quaternion, F, D_f, dF, tool_result)
            for item in evidence_items[: max(1, top_k)]
        ]
        hamilton_trace = self._compose_trace(base_quaternion, relation_states)

        relation_support = self._mean(
            attribute.value
            for state in relation_states
            for attribute in state.attributes
            if attribute.name in {"relevance", "theorem_shape_match", "symbol_library_match"}
        )
        verifier_friction = self._verifier_friction(tool_result)
        recommendation = self._recommend(relation_support, F, dF, verifier_friction)

        return {
            "status": "success",
            "audit_type": "plithogenic_quaternion_relation_audit",
            "scores": {
                "T": T,
                "I_system_S": I_system_S,
                "D_f": D_f,
                "dF": dF,
                "F": F,
                "i_fractal": i_fractal,
            },
            "quaternion_contract": {
                "q": "q=(T,I_system_S,D_f,dF)",
                "F": "external falsity/opposition damping coefficient",
                "i_fractal": "derived measure; never compressed into q",
                "hierarchy": "I -> I_system^S -> D_f -> dF -> i_fractal",
            },
            "normalized_quaternion": base_quaternion.to_dict(),
            "relations": [state.to_dict() for state in relation_states],
            "hamilton_trace": hamilton_trace,
            "recommendation": recommendation,
            "disclaimer": "Classical retrieval relation audit only; this is not quantum computation and not a formal proof.",
        }

    def _build_relation_state(
        self,
        query: str,
        item: Dict[str, Any],
        base_quaternion: Quaternion,
        falsity: float,
        D_f: float,
        dF: float,
        tool_result: Dict[str, Any],
    ) -> RetrievalRelationState:
        evidence_text = str(item.get("text") or "")
        relevance = self._token_overlap(query, evidence_text)
        theorem_shape = self._marker_score(evidence_text, ("theorem", "proof", "environ", "begin", "end;", "definition", "lemma"))
        symbol_match = self._marker_score(evidence_text, MIZAR_MARKERS)
        contradiction = max(D_f, self._marker_score(evidence_text, ("contradiction", "failure", "error", "reject", "invalid")))
        verifier_friction = max(dF, self._verifier_friction(tool_result))

        attributes = [
            self._attribute("relevance", relevance, 0.3),
            self._attribute("theorem_shape_match", theorem_shape, 0.22),
            self._attribute("symbol_library_match", symbol_match, 0.18),
            self._attribute("contradiction", contradiction, 0.15, inverted=True),
            self._attribute("verifier_friction", verifier_friction, 0.15, inverted=True),
        ]

        support = _clamp((relevance * 0.4) + (theorem_shape * 0.3) + (symbol_match * 0.3))
        relation = Quaternion(
            _clamp((base_quaternion.w + support) / 2),
            _clamp(max(base_quaternion.x, 1.0 - support) * 0.75),
            _clamp(max(base_quaternion.y, contradiction)),
            _clamp(max(base_quaternion.z, verifier_friction)),
        ).normalize()

        return RetrievalRelationState(
            query=query,
            evidence_id=str(item.get("id") or "evidence"),
            relation_quaternion=relation,
            falsity_damping=_clamp(1.0 - falsity),
            attributes=attributes,
            source_metadata=dict(item.get("metadata") or {}),
        )

    def _attribute(self, name: str, value: float, weight: float, *, inverted: bool = False) -> PlithogenicAttribute:
        value = _clamp(value)
        dominant = 0.0 if inverted else 1.0
        contradiction = abs(dominant - value)
        return PlithogenicAttribute(name, value, dominant, _clamp(contradiction), weight)

    def _compose_trace(self, base_quaternion: Quaternion, states: Iterable[RetrievalRelationState]) -> List[Dict[str, Any]]:
        accumulator = Quaternion.identity()
        trace: List[Dict[str, Any]] = [
            {
                "step": 0,
                "evidence_id": "identity",
                "input_quaternion": accumulator.to_dict(),
                "accumulator": accumulator.to_dict(),
            }
        ]
        for index, state in enumerate(states, start=1):
            weighted = state.weighted_quaternion()
            accumulator = accumulator.hamilton(weighted).normalize(base_quaternion)
            trace.append(
                {
                    "step": index,
                    "evidence_id": state.evidence_id,
                    "input_quaternion": weighted.to_dict(),
                    "accumulator": accumulator.to_dict(),
                }
            )
        return trace

    def _extract_evidence(self, retrieval: Any, context: str, top_k: int) -> List[Dict[str, Any]]:
        evidence: List[Dict[str, Any]] = []
        self._walk_retrieval(retrieval, evidence)
        if context.strip():
            evidence.append({"id": "rag_context", "text": context, "metadata": {"source": "rag_context"}})
        return evidence[: max(1, top_k)]

    def _walk_retrieval(self, value: Any, evidence: List[Dict[str, Any]]) -> None:
        if value is None:
            return
        if isinstance(value, str):
            if value.strip():
                evidence.append({"id": f"evidence_{len(evidence) + 1}", "text": value, "metadata": {"source": "string"}})
            return
        if isinstance(value, list):
            for item in value:
                self._walk_retrieval(item, evidence)
            return
        if not isinstance(value, dict):
            return

        text = value.get("text") or value.get("content") or value.get("document") or value.get("passage") or value.get("body")
        if text:
            evidence.append(
                {
                    "id": value.get("id") or value.get("doc_id") or value.get("document_id") or f"evidence_{len(evidence) + 1}",
                    "text": str(text),
                    "metadata": {key: val for key, val in value.items() if key not in {"text", "content", "document", "passage", "body"}},
                }
            )

        for key in ("results", "retrieved_docs", "docs", "documents", "passages", "items"):
            if key in value:
                self._walk_retrieval(value[key], evidence)

    def _token_overlap(self, query: str, evidence: str) -> float:
        query_tokens = _tokens(query)
        evidence_tokens = _tokens(evidence)
        if not query_tokens or not evidence_tokens:
            return 0.0
        return _clamp(len(query_tokens & evidence_tokens) / max(1, len(query_tokens)))

    def _marker_score(self, text: str, markers: Iterable[str]) -> float:
        lowered = (text or "").lower()
        marker_list = tuple(markers)
        hits = sum(1 for marker in marker_list if marker.lower() in lowered)
        return _clamp(hits / max(1, min(5, len(marker_list))))

    def _verifier_friction(self, tool_result: Dict[str, Any]) -> float:
        status = str(tool_result.get("status") or "").lower()
        errors = tool_result.get("errors")
        error_count = len(errors) if isinstance(errors, list) else 0
        return _clamp((0.45 if status == "failure" else 0.0) + min(0.45, error_count * 0.1))

    def _mean(self, values: Iterable[float]) -> float:
        collected = list(values)
        if not collected:
            return 0.0
        return _clamp(sum(collected) / len(collected))

    def _recommend(self, relation_support: float, falsity: float, dF: float, verifier_friction: float) -> str:
        if max(dF, verifier_friction) >= 0.5:
            return "inspect_mizar_errors"
        if falsity >= 0.55:
            return "avoid_using_current_context"
        if relation_support >= 0.65:
            return "use_retrieval_context_then_verify"
        return "retrieve_more_or_ask_clarification"
