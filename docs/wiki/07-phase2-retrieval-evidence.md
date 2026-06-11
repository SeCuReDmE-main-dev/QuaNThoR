# Phase 2 Retrieval Evidence

Phase 2 measures HippoRAG retrieval behavior against the Phase 1 educational Mizar dataset.

The runner is:

```powershell
python scripts/run_phase2_relation_dynamics.py --quanthor-url http://localhost:5050
```

Current Phase 2 policy: use Ollama Cloud for LLM inference and do not activate a local Gemma path yet.

```powershell
$env:OLLAMA_CLOUD_TOKEN = "<redacted token from C:\Users\jeans\.openclaw\workspace\.env>"
$env:HIPPORAG_LLM_BASE_URL = "https://ollama.com/v1"
$env:HIPPORAG_LLM_MODEL = "gemma4:31b"
```

The OpenAI Python SDK may still be used by HippoRAG as a protocol client, but this configuration targets Ollama Cloud and does not require a paid OpenAI API key.

Do not activate the local Gemma path during Phase 2 unless explicitly approved. The future local candidate is `gemma4:12b-it-qat`, but the current machine may not be a good runtime target.

Known blocker as of the first Phase 2 run: Ollama Cloud chat works with `gemma4:31b`, but `https://ollama.com/v1/embeddings` returned `404` for `nomic-embed-text`. HippoRAG retrieval still needs an embedding endpoint before the retrieval evidence gate can pass.

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
