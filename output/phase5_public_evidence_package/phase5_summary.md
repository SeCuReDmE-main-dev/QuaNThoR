# Phase 5 Public Evidence Package

Status: `drafted`
Date: `2026-06-11`

QuaNThoR is the public evidence lab for RFC #181. It is not presented as a required dependency for HippoRAG maintainers.

## Public References

- RFC issue: https://github.com/OSU-NLP-Group/HippoRAG/issues/181
- Single upstream PR gate: https://github.com/OSU-NLP-Group/HippoRAG/pull/182
- HippoRAG fork: https://github.com/SeCuReDmE-main-dev/hipporag-case-study
- QuaNThoR: https://github.com/SeCuReDmE-main-dev/QuaNThoR

## Evidence Inventory

| Phase | Local path | Role |
| --- | --- | --- |
| Phase 1 | `examples/mizar/phase1_relation_dynamics/` | Educational Mizar seed dataset |
| Phase 2 | `output/phase2_relation_dynamics/` | Retrieval, routing, and verification baseline |
| Phase 3 | `output/phase3_relation_auditor/` | Neutrosophic and plithogenic quaternion relation audit |
| Phase 5 | `output/phase5_public_evidence_package/` | Reviewer handoff and evidence map |

## What Is Proven

- The educational seed dataset exists and is structured.
- Phase 2 produced 10 retrieval rows, 10 route rows, and 10 verification rows.
- Phase 3 produced 10 neutrosophic rows and 10 plithogenic quaternion rows.
- The hierarchy `I -> I_system^S -> D_f -> dF -> i_fractal` was preserved.
- The auditor keeps formal truth authority with Mizar.

## What Is Observed

- Retrieval evidence can be converted into a structured relation trace.
- The relation trace can expose verifier friction, contradiction, indeterminacy, and channel conflict in a way that a single score does not explain by itself.
- The current evidence is promising enough to continue the RFC discussion, but not enough to claim performance gain.

## What Remains Hypothesis

- Whether the trace predicts verifier friction better than scalar scores on a larger dataset.
- Whether HippoRAG maintainers prefer a hook, metadata-only trace, or separate evaluation adapter.
- Whether relation dynamics should ever influence ranking rather than remain trace-only.

## Not Measured

- Large-scale benchmark performance.
- Maintainer acceptance.
- Runtime overhead on production HippoRAG corpora.
- Any quantum-computation behavior.

## Validation Commands

Use the standard QuaNThoR validation gate:

```powershell
python -m pytest -q
python -m compileall -q src scripts
python scripts/docgen.py check
python scripts/docgen.py build
docker compose config --quiet
```
