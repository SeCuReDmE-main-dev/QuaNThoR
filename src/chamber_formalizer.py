"""Conservative semantic formalizer for FNP-QNN visual chamber requests.

QuaNThoR can organize human intent into the fixed ten-carrier vocabulary.  It
never assigns numerical carrier values, runs FNP-QNN, or imitates Synthia's
admission decision.
"""

from __future__ import annotations

from typing import Any, Mapping


REQUIRED_CARRIERS = (
    "I_source",
    "I_flavor",
    "I_mass",
    "I_mix",
    "I_phase",
    "I_medium",
    "I_interaction",
    "I_secondary",
    "I_detector",
    "I_uncertainty",
)
HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"

_LAYER_MAP = (
    ("source", ("I_source",), "origin carrier"),
    ("propagation", ("I_flavor", "I_mass", "I_mix", "I_phase"), "propagation configuration"),
    ("medium", ("I_medium",), "medium context"),
    ("interaction", ("I_interaction",), "interaction context"),
    ("projection", ("I_secondary", "I_detector"), "secondary response and detector projection"),
    ("uncertainty", ("I_uncertainty",), "uncertainty envelope"),
)


def chamber_formalizer_status() -> dict[str, object]:
    return {
        "status": "ready",
        "formalizer": "QuaNThoR native chamber formalizer",
        "admission_authority": "Synthia",
        "does_not": ["assign carrier values", "admit a chamber", "compute FNP-QNN results"],
        "required_carriers": list(REQUIRED_CARRIERS),
        "hierarchy": HIERARCHY,
    }


def formalize_chamber_request(text: str, candidate: Mapping[str, Any] | None = None) -> dict[str, object]:
    """Produce a fillable, reviewable ten-carrier proposal from user intent."""

    intent = str(text or "").strip()
    supplied = candidate if isinstance(candidate, Mapping) else {}
    submitted = supplied.get("carriers") if isinstance(supplied.get("carriers"), list) else []
    by_name = {
        str(item.get("name", "")).strip(): dict(item)
        for item in submitted
        if isinstance(item, Mapping) and str(item.get("name", "")).strip()
    }
    unknown = sorted(set(by_name).difference(REQUIRED_CARRIERS))
    missing = [name for name in REQUIRED_CARRIERS if name not in by_name]
    proposal = {
        "carrier_order": list(REQUIRED_CARRIERS),
        "carrier_count": len(by_name),
        "semantic_layers": [
            {"layer_id": layer_id, "carrier_names": list(names), "meaning": meaning}
            for layer_id, names, meaning in _LAYER_MAP
        ],
        "carriers": [
            {
                "name": name,
                "role": by_name.get(name, {}).get("role", ""),
                "source_fields": by_name.get(name, {}).get("source_fields", []),
                "value_status": "provided" if name in by_name else "required_from_user",
            }
            for name in REQUIRED_CARRIERS
        ],
    }
    has_intent = bool(intent)
    ready = has_intent and not missing and not unknown
    return {
        "status": "ready_for_synthia_admission" if ready else "needs_clarification",
        "intent": intent,
        "proposal": proposal,
        "missing_carriers": missing,
        "unknown_carriers": unknown,
        "clarifying_questions": _questions(intent, missing, unknown),
        "handoff": {
            "next_authority": "Synthia",
            "required_action": "validate the complete carrier packet before FNP-QNN creates the visual chamber",
            "fallback": "Codex/Gemini may diagnose or refine wording only; they cannot admit the chamber.",
        },
        "hierarchy": HIERARCHY,
        "boundary": "Formalization only. No physical, clinical, or proof authority is claimed.",
    }


def _questions(intent: str, missing: list[str], unknown: list[str]) -> list[str]:
    questions: list[str] = []
    if not intent:
        questions.append("Describe the chamber intent and the source context to formalize.")
    if missing:
        questions.append("Provide roles and source fields for: " + ", ".join(missing) + ".")
    if unknown:
        questions.append("Remove or remap unsupported carriers: " + ", ".join(unknown) + ".")
    if not questions:
        questions.append("Send the complete proposal to Synthia for admission; QuaNThoR does not approve it.")
    return questions
