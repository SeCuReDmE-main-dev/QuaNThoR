import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_phase3_runner_builds_relation_audit_outputs(tmp_path):
    output_dir = tmp_path / "phase3"
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_phase3_relation_auditor.py"),
        "--phase2-dir",
        str(ROOT / "output" / "phase2_relation_dynamics"),
        "--output-dir",
        str(output_dir),
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=60)

    assert result.returncode == 0, result.stderr
    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    trace_rows = [
        json.loads(line)
        for line in (output_dir / "cross_system_trace.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    quaternion_rows = [
        json.loads(line)
        for line in (output_dir / "plithogenic_quaternion_results.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert manifest["status"] == "completed"
    assert manifest["query_count"] == 10
    assert manifest["invariants"]["hierarchy"] == "I -> I_system^S -> D_f -> dF -> i_fractal"
    assert manifest["invariants"]["dF_separate_from_I_system_S"] is True
    assert manifest["expected_actual_conflicts"] >= 1
    assert len(trace_rows) == 10
    assert len(quaternion_rows) == 10

    first_scores = trace_rows[0]["scores"]
    assert "I_system_S" in first_scores
    assert "dF" in first_scores
    assert first_scores["I_system_S"] != first_scores["dF"]
