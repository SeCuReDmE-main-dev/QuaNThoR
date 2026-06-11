# Phase 2 Retrieval Evidence

Phase 2 measures HippoRAG retrieval behavior against the Phase 1 educational Mizar dataset.

The runner is:

```powershell
python scripts/run_phase2_relation_dynamics.py --quanthor-url http://localhost:5050
```

Outputs are written under:

```text
output/phase2_relation_dynamics/
```

Expected files:

- `run_manifest.json`
- `retrieval_results.jsonl`
- `route_results.jsonl`
- `verification_results.jsonl`
- `phase2_summary.md`

## Rules

- HippoRAG retrieval is evidence support, not formal proof.
- Mizar remains authoritative for formal validity.
- Unavailable QuaNThoR or HippoRAG services must be recorded as controlled skips.
- No performance claim is made in Phase 2.
- Phase 3 compares the Phase 2 retrieval rows with neutrosophic and plithogenic quaternion audit outputs.
