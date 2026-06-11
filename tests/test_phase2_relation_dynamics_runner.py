import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_phase2_runner_records_controlled_skip(tmp_path):
    output_dir = tmp_path / "phase2"
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_phase2_relation_dynamics.py"),
        "--quanthor-url",
        "http://127.0.0.1:9",
        "--timeout",
        "0.2",
        "--output-dir",
        str(output_dir),
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=20)

    assert result.returncode == 0, result.stderr
    manifest_path = output_dir / "run_manifest.json"
    summary_path = output_dir / "phase2_summary.md"
    retrieval_path = output_dir / "retrieval_results.jsonl"
    route_path = output_dir / "route_results.jsonl"
    verification_path = output_dir / "verification_results.jsonl"

    assert manifest_path.exists()
    assert summary_path.exists()
    assert retrieval_path.exists()
    assert route_path.exists()
    assert verification_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "controlled_skip"
    assert manifest["query_count"] == 10
    assert manifest["document_count"] == 10
    assert manifest["controlled_skips"][0]["component"] == "quanthor"
    assert "retrieval improvement" in summary_path.read_text(encoding="utf-8")
