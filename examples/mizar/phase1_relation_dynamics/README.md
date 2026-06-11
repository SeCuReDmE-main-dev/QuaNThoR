# Phase 1 Relation Dynamics Mizar Dataset

This dataset is the first public QuaNThoR evidence package for the HippoRAG relation-dynamics RFC.

It is intentionally small, readable, and education-facing. The goal is not to prove that retrieval improves formal proof generation yet. The goal is to create a stable seed set where retrieval support, indeterminacy, contradiction, channel conflict, and verification friction can be observed without changing HippoRAG upstream behavior.

## Contents

- `queries.jsonl`: ten student-readable theorem/proof requests.
- `expected_outcomes.json`: expected verifier and retrieval/audit behavior.
- `retrieval_notes.md`: notes for interpreting retrieval and audit outputs.
- `proofs/valid/*.miz`: minimal valid Mizar articles.
- `proofs/invalid/*.miz`: intentionally invalid or incomplete Mizar articles.

## Relation Dynamics Focus Values

- `support`: retrieved context should help the proof path.
- `indeterminacy`: the request is underspecified or missing library/context.
- `contradiction`: retrieved or drafted material is expected to conflict with the verifier.
- `channel_conflict`: natural-language plausibility and formal shape may disagree.
- `verification_friction`: the main signal should be Mizar verifier failure or missing formal detail.

## Educational Intent

Each example is meant to help a student or professor inspect why a proof path helps, fails, or needs clarification. Mizar remains the authority for formal truth. Retrieval and audits are explanatory tools, not proof substitutes.
