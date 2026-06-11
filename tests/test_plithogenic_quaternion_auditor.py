from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app import app  # noqa: E402
from plithogenic_quaternion_auditor import (  # noqa: E402
    PlithogenicAttribute,
    PlithogenicQuaternionAuditor,
    Quaternion,
)


def test_hamilton_identity_and_non_commutativity():
    q1 = Quaternion(0.5, 0.5, 0.5, 0.5)
    q2 = Quaternion(0.1, 0.2, 0.3, 0.4)

    assert Quaternion.identity().hamilton(q1) == q1
    assert q1.hamilton(Quaternion.identity()) == q1
    assert q1.hamilton(q2) != q2.hamilton(q1)


def test_normalization_and_zero_vector_fallback():
    normalized = Quaternion(2.0, 0.0, 0.0, 0.0).normalize()
    assert math.isclose(normalized.norm(), 1.0)
    assert Quaternion(0.0, 0.0, 0.0, 0.0).normalize() == Quaternion.identity()


def test_plithogenic_contradiction_weighting():
    attribute = PlithogenicAttribute(
        name="relevance",
        value=0.75,
        dominant_value=1.0,
        contradiction_degree=0.25,
        weight=0.4,
    )
    assert attribute.effective_weight() == 0.3
    assert attribute.weighted_value() == 0.225


def test_auditor_preserves_df_separate_from_i_system_s():
    audit = PlithogenicQuaternionAuditor().audit(
        "prove theorem TopSpace",
        retrieval=[{"id": "doc1", "text": "theorem Th1: proof end; PRE_TOPC example"}],
        neutrosophic_audit={
            "scores": {
                "T": 0.6,
                "I_system_S": 0.1,
                "D_f": 0.2,
                "dF": 0.7,
                "F": 0.1,
                "i_fractal": 0.3333,
            }
        },
        tool_result={"status": "failure", "errors": [{"line": 1}]},
    )

    assert audit["quaternion_contract"]["hierarchy"] == "I -> I_system^S -> D_f -> dF -> i_fractal"
    assert audit["scores"]["I_system_S"] == 0.1
    assert audit["scores"]["dF"] == 0.7
    assert audit["scores"]["i_fractal"] == 0.3333
    assert audit["recommendation"] == "inspect_mizar_errors"


def test_auditor_is_deterministic_without_optional_dependencies():
    auditor = PlithogenicQuaternionAuditor()
    kwargs = {
        "text": "formalize a theorem about subsets",
        "retrieval": [{"id": "doc1", "text": "definition subset theorem proof end;"}],
        "neutrosophic_audit": {"scores": {"T": 0.5, "I_system_S": 0.2, "D_f": 0.1, "dF": 0.0, "F": 0.0}},
        "tool_result": {"status": "success", "errors": []},
    }
    assert auditor.audit(**kwargs) == auditor.audit(**kwargs)


def test_plithogenic_quaternion_endpoint_stable():
    client = app.test_client()
    response = client.post(
        "/audit/plithogenic-quaternion",
        json={
            "text": "prove a theorem about topological spaces",
            "decision": {"route": "draft_mizar", "confidence": 0.8},
            "retrieval": [{"id": "mizar-doc", "text": "theorem Th1: proof end; PRE_TOPC"}],
            "tool_result": {"status": "success", "errors": []},
            "neutrosophic_audit": {"scores": {"T": 0.7, "I_system_S": 0.1, "D_f": 0.1, "dF": 0.0, "F": 0.0}},
        },
    )

    payload = response.get_json()
    assert response.status_code == 200
    assert payload["status"] == "success"
    assert payload["audit_type"] == "plithogenic_quaternion_relation_audit"
    assert payload["relations"][0]["evidence_id"] == "mizar-doc"
    assert payload["quaternion_contract"]["q"] == "q=(T,I_system_S,D_f,dF)"


def test_route_unchanged_without_plithogenic_flag():
    client = app.test_client()
    response = client.post("/route", json={"text": "explain this proof", "execute": False})
    payload = response.get_json()

    assert response.status_code == 200
    assert "plithogenic_quaternion_audit" not in payload
