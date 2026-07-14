from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app import app  # noqa: E402
from chamber_formalizer import REQUIRED_CARRIERS, formalize_chamber_request  # noqa: E402


def _complete_candidate():
    return {
        "carriers": [
            {"name": name, "role": f"role:{name}", "source_fields": [f"field:{name}"]}
            for name in REQUIRED_CARRIERS
        ]
    }


def test_formalizer_requires_all_fixed_carriers_before_synthia_handoff():
    result = formalize_chamber_request("visualize an admitted chamber", _complete_candidate())

    assert result["status"] == "ready_for_synthia_admission"
    assert result["proposal"]["carrier_order"] == list(REQUIRED_CARRIERS)
    assert result["handoff"]["next_authority"] == "Synthia"
    assert result["hierarchy"] == "I -> I_system^S -> D_f -> dF -> i_fractal"


def test_formalizer_does_not_invent_missing_carriers():
    result = formalize_chamber_request("make a chamber", {"carriers": [{"name": "I_source"}]})

    assert result["status"] == "needs_clarification"
    assert "I_flavor" in result["missing_carriers"]
    assert result["proposal"]["carriers"][1]["value_status"] == "required_from_user"


def test_chamber_formalize_endpoint_keeps_synthia_as_authority():
    response = app.test_client().post(
        "/chamber/formalize",
        json={"text": "create a bounded chamber", "candidate": _complete_candidate()},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "ready_for_synthia_admission"
    assert payload["handoff"]["next_authority"] == "Synthia"
