"""Run Phase 3 relation-auditor evidence over Phase 2 outputs.

The script is offline and deterministic. It does not call an LLM, does not
mutate HippoRAG, and keeps Mizar verification as the formal authority.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neutrosophic_auditor import NeutrosophicAuditor  # noqa: E402
from plithogenic_quaternion_auditor import PlithogenicQuaternionAuditor  # noqa: E402


PHASE1_DIR = ROOT / "examples" / "mizar" / "phase1_relation_dynamics"
PHASE2_DIR = ROOT / "output" / "phase2_relation_dynamics"
DEFAULT_OUTPUT_DIR = ROOT / "output" / "phase3_relation_auditor"


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def target_to_verification(target: str, verification_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    target_slug = str(target or "").lower().replace("-", "_")
    for row in verification_rows:
        if target_slug and target_slug in str(row.get("id", "")).lower():
            return row
    return {}


def route_decision(route_payload: Dict[str, Any]) -> Dict[str, Any]:
    decision = route_payload.get("decision")
    if isinstance(decision, dict):
        return decision
    return {
        "route": route_payload.get("route"),
        "confidence": route_payload.get("confidence", 0.5),
        "reason": route_payload.get("reason", ""),
    }


def retrieval_docs(retrieval_payload: Dict[str, Any]) -> List[str]:
    results = retrieval_payload.get("results") if isinstance(retrieval_payload, dict) else []
    if not results:
        return []
    first = results[0] if isinstance(results[0], dict) else {}
    return [str(doc) for doc in first.get("docs") or []]


def retrieval_top_score(retrieval_payload: Dict[str, Any]) -> float:
    results = retrieval_payload.get("results") if isinstance(retrieval_payload, dict) else []
    if not results:
        return 0.0
    first = results[0] if isinstance(results[0], dict) else {}
    scores = first.get("doc_scores") or []
    try:
        return float(scores[0]) if scores else 0.0
    except (TypeError, ValueError):
        return 0.0


def expected_actual_conflict(query: Dict[str, Any], verification_row: Dict[str, Any]) -> bool:
    if not verification_row:
        return False
    expected = str(query.get("expected_verifier_status") or "").lower()
    verification = verification_row.get("verification") if isinstance(verification_row, dict) else {}
    observed = str((verification or {}).get("status") or "").lower()
    if expected == "invalid":
        return observed == "success"
    if expected == "valid":
        return observed not in {"success", "routed"}
    return False


def adjusted_scores(base_scores: Dict[str, Any], *, conflict: bool, retrieval_score: float) -> Dict[str, float]:
    scores = {
        "T": float(base_scores.get("T", 0.0)),
        "I_system_S": float(base_scores.get("I_system_S", 0.0)),
        "D_f": float(base_scores.get("D_f", 0.0)),
        "dF": float(base_scores.get("dF", 0.0)),
        "F": float(base_scores.get("F", 0.0)),
        "i_fractal": float(base_scores.get("i_fractal", 0.0)),
    }
    if conflict:
        scores["D_f"] = max(scores["D_f"], 0.55)
        scores["F"] = max(scores["F"], 0.35)
    if retrieval_score < 0.05:
        scores["I_system_S"] = max(scores["I_system_S"], 0.35)
    scores["i_fractal"] = round((scores["I_system_S"] + scores["D_f"] + scores["dF"]) / 3, 4)
    return {key: round(value, 4) for key, value in scores.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase2-dir", default=str(PHASE2_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    phase2_dir = Path(args.phase2_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    queries = read_jsonl(PHASE1_DIR / "queries.jsonl")
    phase2_manifest = read_json(phase2_dir / "run_manifest.json")
    retrieval_rows = {row["id"]: row for row in read_jsonl(phase2_dir / "retrieval_results.jsonl")}
    route_rows = {row["id"]: row for row in read_jsonl(phase2_dir / "route_results.jsonl")}
    verification_rows = read_jsonl(phase2_dir / "verification_results.jsonl")

    neutrosophic = NeutrosophicAuditor()
    quaternion = PlithogenicQuaternionAuditor()

    neutro_rows: List[Dict[str, Any]] = []
    quaternion_rows: List[Dict[str, Any]] = []
    trace_rows: List[Dict[str, Any]] = []

    for query in queries:
        qid = query["id"]
        retrieval = retrieval_rows.get(qid, {}).get("retrieval", {})
        route = route_rows.get(qid, {}).get("route", {})
        verification_row = target_to_verification(query.get("mizar_target", ""), verification_rows)
        verification = verification_row.get("verification", {})
        missing_mapping = not bool(verification_row)
        docs = retrieval_docs(retrieval)
        rag_context = "\n\n".join(docs[:3])
        conflict = expected_actual_conflict(query, verification_row)
        top_score = retrieval_top_score(retrieval)

        neutro = neutrosophic.audit(
            query["student_query"],
            route_decision=route_decision(route),
            rag_context=rag_context,
            tool_result=verification,
        )
        neutro["phase3_adjusted_scores"] = adjusted_scores(
            neutro["scores"], conflict=conflict, retrieval_score=top_score
        )
        neutro["phase3_expected_actual_conflict"] = conflict
        neutro["phase3_missing_verification_mapping"] = missing_mapping
        neutro["phase3_relation_dynamics_focus"] = query.get("relation_dynamics_focus")

        quaternion_audit = quaternion.audit(
            query["student_query"],
            retrieval=retrieval,
            neutrosophic_audit={"scores": neutro["phase3_adjusted_scores"]},
            tool_result=verification,
            top_k=3,
        )

        neutro_rows.append({"id": qid, "query": query["student_query"], "neutrosophic_audit": neutro})
        quaternion_rows.append({"id": qid, "query": query["student_query"], "plithogenic_quaternion_audit": quaternion_audit})
        trace_rows.append(
            {
                "id": qid,
                "expected_verifier_status": query.get("expected_verifier_status"),
                "observed_verifier_status": verification.get("status"),
                "expected_actual_conflict": conflict,
                "missing_verification_mapping": missing_mapping,
                "top_retrieval_score": round(top_score, 4),
                "route": route_decision(route).get("route"),
                "recommendation": quaternion_audit.get("recommendation"),
                "scores": neutro["phase3_adjusted_scores"],
            }
        )

    manifest = {
        "phase": "phase3_relation_auditor_hardening",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "phase2_status": phase2_manifest.get("status"),
        "output_dir": str(output_dir),
        "python": sys.version,
        "platform": platform.platform(),
        "query_count": len(queries),
        "neutrosophic_rows": len(neutro_rows),
        "plithogenic_quaternion_rows": len(quaternion_rows),
        "expected_actual_conflicts": sum(1 for row in trace_rows if row["expected_actual_conflict"]),
        "missing_verification_mappings": sum(1 for row in trace_rows if row["missing_verification_mapping"]),
        "status": "completed",
        "invariants": {
            "hierarchy": "I -> I_system^S -> D_f -> dF -> i_fractal",
            "dF_separate_from_I_system_S": True,
            "no_quantum_computation_claim": True,
        },
    }

    (output_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_jsonl(output_dir / "neutrosophic_audit_results.jsonl", neutro_rows)
    write_jsonl(output_dir / "plithogenic_quaternion_results.jsonl", quaternion_rows)
    write_jsonl(output_dir / "cross_system_trace.jsonl", trace_rows)
    write_summary(output_dir, manifest, trace_rows)
    return 0


def write_summary(output_dir: Path, manifest: Dict[str, Any], trace_rows: List[Dict[str, Any]]) -> None:
    recommendation_counts: Dict[str, int] = {}
    for row in trace_rows:
        recommendation = str(row.get("recommendation") or "unknown")
        recommendation_counts[recommendation] = recommendation_counts.get(recommendation, 0) + 1

    lines = [
        "# Phase 3 Relation Auditor Summary",
        "",
        f"Status: `{manifest['status']}`",
        f"Created: `{manifest['created_at']}`",
        f"Phase 2 status consumed: `{manifest['phase2_status']}`",
        "",
        "## Counts",
        "",
        f"- Queries audited: {manifest['query_count']}",
        f"- Neutrosophic rows: {manifest['neutrosophic_rows']}",
        f"- Plithogenic quaternion rows: {manifest['plithogenic_quaternion_rows']}",
        f"- Expected-vs-observed verifier conflicts: {manifest['expected_actual_conflicts']}",
        f"- Missing verifier mappings: {manifest['missing_verification_mappings']}",
        "",
        "## Recommendations",
        "",
    ]
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(recommendation_counts.items()))
    lines.extend(
        [
            "",
            "## Invariants",
            "",
            "- `I -> I_system^S -> D_f -> dF -> i_fractal` preserved.",
            "- `dF` remains separate from `I_system_S`.",
            "- The quaternion trace is classical relation dynamics, not quantum computation and not formal proof.",
            "",
        ]
    )
    (output_dir / "phase3_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
