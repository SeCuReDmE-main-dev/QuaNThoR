import json
from pathlib import Path


DATASET_DIR = Path(__file__).resolve().parents[1] / "examples" / "mizar" / "phase1_relation_dynamics"

REQUIRED_FIELDS = {
    "id",
    "student_query",
    "mizar_target",
    "expected_retrieval_support",
    "expected_failure_mode",
    "education_note",
    "expected_verifier_status",
    "relation_dynamics_focus",
}

FOCUS_VALUES = {
    "support",
    "indeterminacy",
    "contradiction",
    "channel_conflict",
    "verification_friction",
}


def test_phase1_dataset_shape():
    queries_path = DATASET_DIR / "queries.jsonl"
    expected_path = DATASET_DIR / "expected_outcomes.json"

    assert queries_path.exists()
    assert expected_path.exists()

    records = [json.loads(line) for line in queries_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(records) == 10
    assert len({record["id"] for record in records}) == 10

    for record in records:
        assert REQUIRED_FIELDS <= set(record)
        assert record["relation_dynamics_focus"] in FOCUS_VALUES
        assert record["student_query"].strip()
        assert record["education_note"].strip()

    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert expected["expected_counts"]["valid_proofs"] == 5
    assert expected["expected_counts"]["invalid_or_incomplete_proofs"] == 5
    assert expected["expected_counts"]["student_queries"] == 10


def test_phase1_dataset_mizar_fixture_counts():
    valid_files = sorted((DATASET_DIR / "proofs" / "valid").glob("*.miz"))
    invalid_files = sorted((DATASET_DIR / "proofs" / "invalid").glob("*.miz"))

    assert len(valid_files) == 5
    assert len(invalid_files) == 5

    for path in valid_files + invalid_files:
        text = path.read_text(encoding="utf-8")
        assert "environ" in text
        assert "begin" in text
        assert "theorem" in text
