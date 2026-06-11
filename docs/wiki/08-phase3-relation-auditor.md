# Phase 3 Relation Auditor

Phase 3 applies the local neutrosophic and plithogenic quaternion auditors to the completed Phase 2 retrieval evidence.

Run:

```powershell
python scripts/run_phase3_relation_auditor.py
```

Outputs are written under:

```text
output/phase3_relation_auditor/
```

Expected files:

- `run_manifest.json`
- `neutrosophic_audit_results.jsonl`
- `plithogenic_quaternion_results.jsonl`
- `cross_system_trace.jsonl`
- `phase3_summary.md`

## Current Result

Latest completed run:

- Queries audited: 10
- Neutrosophic rows: 10
- Plithogenic quaternion rows: 10
- Expected-vs-observed verifier conflicts: 4
- Missing verifier mappings: 3

The conflicts are evidence for audit hardening, not proof of retrieval failure. They show where the dataset expectation, retrieved support, route decision, and verifier observation disagree.

## Invariants

- `I -> I_system^S -> D_f -> dF -> i_fractal` is preserved.
- `dF` remains separate from `I_system_S`.
- `F` remains an external damping/opposition coefficient.
- The quaternion trace is classical relation dynamics, not quantum computation.
- Mizar remains the authority for formal proof validity.

## Phase 3 Purpose

Phase 3 does not change HippoRAG upstream behavior. It prepares evidence for whether structured retrieval relation dynamics can explain verification friction better than a scalar retrieval score alone.
