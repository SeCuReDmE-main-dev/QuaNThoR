"""Run Phase 2 HippoRAG retrieval evidence against the Phase 1 Mizar dataset.

The script is intentionally conservative:
- It never mutates HippoRAG upstream code.
- It records unavailable services as controlled skips.
- It writes JSON/JSONL/Markdown evidence for later RFC comments.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

import requests


ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "examples" / "mizar" / "phase1_relation_dynamics"
DEFAULT_OUTPUT_DIR = ROOT / "output" / "phase2_relation_dynamics"


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def post_json(url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    response = requests.post(url, json=payload, timeout=timeout)
    try:
        body = response.json()
    except ValueError:
        body = {"raw_text": response.text}
    body.setdefault("http_status", response.status_code)
    return body


def get_json(url: str, timeout: float) -> Dict[str, Any]:
    response = requests.get(url, timeout=timeout)
    try:
        body = response.json()
    except ValueError:
        body = {"raw_text": response.text}
    body.setdefault("http_status", response.status_code)
    return body


def collect_documents() -> List[Dict[str, str]]:
    docs: List[Dict[str, str]] = []
    for status in ("valid", "invalid"):
        for path in sorted((DATASET_DIR / "proofs" / status).glob("*.miz")):
            docs.append(
                {
                    "id": f"{status}/{path.name}",
                    "status": status,
                    "text": path.read_text(encoding="utf-8"),
                }
            )
    return docs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quanthor-url", default=os.getenv("QUANTHOR_URL", "http://localhost:5050"))
    parser.add_argument("--top-k", type=int, default=int(os.getenv("PHASE2_TOP_K", "3")))
    parser.add_argument("--timeout", type=float, default=float(os.getenv("PHASE2_TIMEOUT_SECONDS", "30")))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument(
        "--skip-route",
        action="store_true",
        help="Skip /route calls when the configured route model would activate a disallowed local model.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    queries = read_jsonl(DATASET_DIR / "queries.jsonl")
    docs = collect_documents()
    now = datetime.now(timezone.utc).isoformat()

    manifest: Dict[str, Any] = {
        "phase": "phase2_hipporag_retrieval_evidence",
        "created_at": now,
        "dataset_dir": str(DATASET_DIR),
        "output_dir": str(output_dir),
        "quanthor_url": args.quanthor_url,
        "top_k": args.top_k,
        "python": sys.version,
        "platform": platform.platform(),
        "query_count": len(queries),
        "document_count": len(docs),
        "route_skipped_by_operator": args.skip_route,
        "status": "started",
        "controlled_skips": [],
    }

    retrieval_rows: List[Dict[str, Any]] = []
    route_rows: List[Dict[str, Any]] = []
    verification_rows: List[Dict[str, Any]] = []

    try:
        health = get_json(f"{args.quanthor_url}/health", args.timeout)
        manifest["quanthor_health"] = health
    except Exception as exc:  # noqa: BLE001 - evidence script records operational state
        manifest["status"] = "controlled_skip"
        manifest["controlled_skips"].append(
            {
                "component": "quanthor",
                "reason": f"QuaNThoR service unavailable at {args.quanthor_url}: {exc}",
            }
        )
        (output_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        write_jsonl(output_dir / "retrieval_results.jsonl", retrieval_rows)
        write_jsonl(output_dir / "route_results.jsonl", route_rows)
        write_jsonl(output_dir / "verification_results.jsonl", verification_rows)
        write_summary(output_dir, manifest, retrieval_rows, route_rows, verification_rows)
        return 0

    try:
        index_payload = {"docs": [doc["text"] for doc in docs]}
        manifest["index_result"] = post_json(f"{args.quanthor_url}/rag/index", index_payload, args.timeout)
    except Exception as exc:  # noqa: BLE001
        manifest["index_result"] = {"status": "controlled_skip", "message": str(exc)}
        manifest["controlled_skips"].append({"component": "hipporag_index", "reason": str(exc)})
    else:
        if manifest["index_result"].get("status") != "success":
            manifest["controlled_skips"].append(
                {
                    "component": "hipporag_index",
                    "reason": manifest["index_result"].get("message", "HippoRAG index did not return success."),
                    "http_status": manifest["index_result"].get("http_status"),
                }
            )

    for query in queries:
        query_id = query["id"]
        text = query["student_query"]

        try:
            retrieval = post_json(
                f"{args.quanthor_url}/rag/retrieve",
                {"query": text, "top_k": args.top_k},
                args.timeout,
            )
        except Exception as exc:  # noqa: BLE001
            retrieval = {"status": "controlled_skip", "message": str(exc)}
        if isinstance(retrieval, dict) and retrieval.get("status") != "success":
            manifest["controlled_skips"].append(
                {
                    "component": "hipporag_retrieve",
                    "id": query_id,
                    "reason": retrieval.get("message", "HippoRAG retrieve did not return success."),
                    "http_status": retrieval.get("http_status"),
                }
            )
        retrieval_rows.append({"id": query_id, "query": text, "retrieval": retrieval})

        if args.skip_route:
            route = {
                "status": "controlled_skip",
                "message": "Route step skipped: current runtime policy forbids activating the resolved local route model.",
            }
            manifest["controlled_skips"].append(
                {
                    "component": "quanthor_route",
                    "id": query_id,
                    "reason": route["message"],
                }
            )
        else:
            try:
                route = post_json(
                    f"{args.quanthor_url}/route",
                    {
                        "text": text,
                        "execute": False,
                        "use_rag": False,
                        "audit_neutrosophy": True,
                        "audit_plithogenic_quaternion": False,
                    },
                    args.timeout,
                )
            except Exception as exc:  # noqa: BLE001
                route = {"status": "controlled_skip", "message": str(exc)}
        route_rows.append({"id": query_id, "query": text, "route": route})

    for doc in docs:
        try:
            verification = post_json(
                f"{args.quanthor_url}/verify",
                {"code": doc["text"]},
                args.timeout,
            )
        except Exception as exc:  # noqa: BLE001
            verification = {"status": "controlled_skip", "message": str(exc)}
        if isinstance(verification, dict) and verification.get("status") in {"controlled_skip", "error"}:
            manifest["controlled_skips"].append(
                {
                    "component": "mizar_verify",
                    "id": doc["id"],
                    "reason": verification.get("message", "Mizar verification did not complete."),
                    "http_status": verification.get("http_status"),
                }
            )
        verification_rows.append({"id": doc["id"], "fixture_status": doc["status"], "verification": verification})

    manifest["status"] = "completed_with_skips" if manifest["controlled_skips"] else "completed"
    (output_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_jsonl(output_dir / "retrieval_results.jsonl", retrieval_rows)
    write_jsonl(output_dir / "route_results.jsonl", route_rows)
    write_jsonl(output_dir / "verification_results.jsonl", verification_rows)
    write_summary(output_dir, manifest, retrieval_rows, route_rows, verification_rows)
    return 0


def count_success(rows: List[Dict[str, Any]], key: str) -> int:
    total = 0
    for row in rows:
        payload = row.get(key, {})
        if isinstance(payload, dict) and payload.get("status") in {"success", "routed"}:
            total += 1
    return total


def write_summary(
    output_dir: Path,
    manifest: Dict[str, Any],
    retrieval_rows: List[Dict[str, Any]],
    route_rows: List[Dict[str, Any]],
    verification_rows: List[Dict[str, Any]],
) -> None:
    lines = [
        "# Phase 2 Retrieval Evidence Summary",
        "",
        f"Status: `{manifest.get('status')}`",
        f"Created: `{manifest.get('created_at')}`",
        f"QuaNThoR URL: `{manifest.get('quanthor_url')}`",
        "",
        "## Counts",
        "",
        f"- Queries: {manifest.get('query_count')}",
        f"- Documents: {manifest.get('document_count')}",
        f"- Retrieval rows: {len(retrieval_rows)}",
        f"- Route rows: {len(route_rows)}",
        f"- Verification rows: {len(verification_rows)}",
        f"- Successful retrieval rows: {count_success(retrieval_rows, 'retrieval')}",
        f"- Successful route rows: {count_success(route_rows, 'route')}",
        "",
        "## Controlled Skips",
        "",
    ]
    skips = manifest.get("controlled_skips") or []
    if skips:
        lines.extend(f"- `{skip.get('component')}`: {skip.get('reason')}" for skip in skips)
    else:
        lines.append("- None recorded.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This file records operational evidence only. It does not claim retrieval improvement.",
            "Mizar verification remains authoritative for formal truth.",
            "Phase 3 must compare these rows with neutrosophic and plithogenic quaternion audit outputs.",
            "",
        ]
    )
    (output_dir / "phase2_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
