# Phase 2 Retrieval Evidence

Phase 2 measures HippoRAG retrieval behavior against the Phase 1 educational Mizar dataset.

The runner is:

```powershell
python scripts/run_phase2_relation_dynamics.py --quanthor-url http://localhost:5050
```

Current Phase 2 policy: use cloud inference for LLM/router work and do not activate a local Gemma path.

```powershell
$env:OLLAMA_CLOUD_TOKEN = "<redacted token from C:\Users\jeans\.openclaw\workspace\.env>"
$env:HIPPORAG_LLM_BASE_URL = "https://ollama.com/v1"
$env:HIPPORAG_LLM_MODEL = "gemma4:31b"
$env:HIPPORAG_EMBEDDING_MODEL = "Transformers/sentence-transformers/all-MiniLM-L6-v2"
$env:OLLAMA_MODEL = "gpt-oss:120b-cloud"
$env:OLLAMA_MIZAR_MODEL = "gpt-oss:120b-cloud"
$env:OLLAMA_ROUTER_MODEL = "gpt-oss:120b-cloud"
```

The OpenAI Python SDK may still be used by HippoRAG as a protocol client, but this configuration targets Ollama Cloud and does not require a paid OpenAI API key.

Do not activate the local Gemma path during Phase 2 unless explicitly approved. The future local candidate is `gemma4:12b-it-qat`, but the current machine may not be a good runtime target.

Embedding decision for the completed Phase 2 run: Ollama Cloud chat works with `gemma4:31b`, but `https://ollama.com/v1/embeddings` returned `404` for embedding models. The native Ollama embeddings endpoint `https://ollama.com/api/embed` is documented for models such as `embeddinggemma`, `qwen3-embedding`, and `all-minilm`, but the current token returned `401` against that direct cloud endpoint. Phase 2 therefore uses the explicit local CPU embedding model `Transformers/sentence-transformers/all-MiniLM-L6-v2`, which is small and does not activate local Gemma.

Route decision for the completed Phase 2 run: the QuaNThoR route/draft/proofread path uses the already configured cloud model `gpt-oss:120b-cloud`, because the native Ollama route path otherwise resolves `gemma4:31b` to the local `gemma4:12b-it-qat` candidate.

Latest completed run: `output/phase2_relation_dynamics/run_manifest.json` reports 10/10 HippoRAG retrieval rows, 10/10 route rows, 10/10 Mizar verification rows, and zero controlled skips.

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
