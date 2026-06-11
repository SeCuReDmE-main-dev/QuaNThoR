# QuaNThoR

QuaNThoR is a containerized Mizar verifier for students and mathematicians. It runs the official Linux Mizar package inside Docker and wraps the verifier output with a short explanation layer.

## What it does

- Verifies full `.miz` articles
- Returns raw verifier output and parsed errors
- Adds a short proof explanation in plain language
- Drafts a conservative Mizar skeleton from a natural-language request
- Routes mixed input to proofreading, Mizar drafting, Mizar verification, or clarification
- Optionally indexes and retrieves Mizar context through HippoRAG
- Can use a remote Ollama server for proofreading through `OLLAMA_BASE_URL`
- In Docker Desktop, defaults to `http://host.docker.internal:11434` so the container can reach the host Ollama service
- Automatically selects the best compatible Ollama model it can reach, then falls back to a safe heuristic if no model is available

## Supported path

- Docker Desktop on Windows
- Host port `5050` by default
- Remote Ollama endpoint through `OLLAMA_BASE_URL`

## Quick start

1. Install Docker Desktop.
2. Leave `OLLAMA_BASE_URL` empty for the default Docker Desktop bridge, or set it to your Ollama endpoint if you want a different server.
3. Run `INSTALL_QUANTHOR.bat`.
4. Run `START_QUANTHOR.bat`.
5. Open `http://localhost:5050`.

## For students

- Paste a complete Mizar article, not a fragment.
- Fix the first verifier error first.
- Re-run after each change so the next failure is easier to read.

## For mathematicians

- `GET /health` reports the active Mizar and Ollama configuration.
- `POST /verify` accepts JSON with a single `code` field.
- `POST /draft` accepts JSON with a `query` field and returns a conservative Mizar draft plus clarifying questions.
- `POST /proofread` accepts JSON with a `text` field and returns corrected prose plus suggestions.
- `POST /route` accepts JSON with `text`, `query`, `prompt`, or `code`; it chooses and runs the right tool by default.
- `GET /rag/status` reports whether HippoRAG is enabled, installed, and initialized.
- `POST /rag/index` accepts `docs`, `documents`, or `text` and adds them to the HippoRAG index.
- `POST /rag/retrieve` accepts `query` and optional `top_k`, then returns retrieved context.
- `POST /rag/qa` accepts `query` and optional `top_k`, then runs HippoRAG retrieval QA.
- `POST /audit/neutrosophy` accepts `text`, `query`, `prompt`, or `code` and returns an operational T/I/F audit.
- `POST /route` can also accept `use_rag: true` for RAG-assisted Mizar drafting and `audit_neutrosophy: true` for workflow auditing.
- The response includes `status`, `errors`, `raw_output`, `ai_assistant`, and `dual_layer_verification`.

Example request:

```json
{
  "code": "environ\n\nbegin\n\ntheorem T1: 1 = 1;\nproof\n  thus 1 = 1;\nend;\n\nend."
}
```

## Configuration

- `OLLAMA_BASE_URL`: remote Ollama server root, for example `https://ollama.example.com`
- `OLLAMA_MIZAR_BASE_URL`: optional separate endpoint for the drafting helper
- `OLLAMA_MODEL`: model name sent to Ollama, default `qwen2.5:7b`
- `OLLAMA_MIZAR_MODEL`: model used for Mizar drafting, default `qwen2.5:7b`
- `OLLAMA_ROUTER_MODEL`: model used to choose `proofread`, `draft_mizar`, `verify_mizar`, or `needs_clarification`; Docker defaults to `mizar-specialist`
- `HIPPORAG_ENABLED`: set to `true` to enable the optional HippoRAG backend, default `false`
- `HIPPORAG_SAVE_DIR`: persistent HippoRAG storage path, default `/app/outputs/hipporag` in Docker
- `HIPPORAG_LLM_MODEL`: LLM name passed to HippoRAG, default `qwen2.5:7b`
- `HIPPORAG_LLM_BASE_URL`: OpenAI-compatible LLM endpoint for HippoRAG
- `HIPPORAG_EMBEDDING_MODEL`: embedding model passed to HippoRAG, default `nvidia/NV-Embed-v2`
- `HIPPORAG_EMBEDDING_BASE_URL`: OpenAI-compatible embedding endpoint for HippoRAG
- `HIPPORAG_TOP_K`: default retrieval count, default `5`
- `HIPPORAG_SERVICE_URL`: optional HippoRAG sidecar URL, for example `http://hipporag:5100`
- `HIPPORAG_REQUEST_TIMEOUT_SECONDS`: timeout for sidecar calls, default `120`
- `MIZAR_TIMEOUT_SECONDS`: verifier timeout in seconds, default `60`
- `QUANTHOR_HOST_PORT`: host port exposed by Docker, default `5050`

If the configured model is not available, the backend falls back to the first compatible model it finds, preferring `gpt-oss:120b-cloud`, then math-focused and multilingual open models.

## Mizar specialist model

The repo includes a ready-to-use Ollama `Modelfile`:

```powershell
ollama create mizar-specialist -f .\models\mizar-specialist\Modelfile
```

Use it with the router and drafter:

```powershell
$env:OLLAMA_ROUTER_MODEL = "mizar-specialist"
$env:OLLAMA_MIZAR_MODEL = "mizar-specialist"
docker compose up --build
```

When a LoRA or QLoRA adapter trained on Mizar examples is ready, add an `ADAPTER` line to `models/mizar-specialist/Modelfile`. The adapter must be trained from the same base model used by `FROM`.

## Optional HippoRAG backend

HippoRAG is not installed in the core Docker image by default. The upstream project documents a Python 3.10 environment, while the QuaNThoR verifier image uses the Mizar-focused runtime. Keeping HippoRAG optional avoids breaking verification for students.

Preferred Docker sidecar path:

```powershell
$env:HIPPORAG_SERVICE_URL = "http://hipporag:5100"
$env:HIPPORAG_LLM_BASE_URL = "http://host.docker.internal:11434/v1"
$env:HIPPORAG_LLM_MODEL = "mizar-specialist"
docker compose --profile hipporag up --build
```

The main backend will proxy `/rag/status`, `/rag/index`, `/rag/retrieve`, and `/rag/qa` to the sidecar.

In-process development path:

Use a dedicated Python 3.10 environment:

```bash
python -m pip install -r requirements-hipporag.txt
```

Then run QuaNThoR with HippoRAG enabled:

```powershell
$env:HIPPORAG_ENABLED = "true"
$env:HIPPORAG_LLM_BASE_URL = "http://host.docker.internal:11434/v1"
$env:HIPPORAG_LLM_MODEL = "mizar-specialist"
docker compose up --build
```

Index examples before retrieval:

```json
{
  "docs": [
    "A Mizar theorem starts with a statement and a proof block.",
    "Use registered requirements and vocabularies in the environ section."
  ]
}
```

## Optional neutrosophic audit

The audit layer is deterministic and dependency-free. It does not prove a theorem and does not replace Mizar. It reports operational evidence for the hierarchy:

```text
I -> I_system^S -> D_f -> dF -> i_fractal
```

Standalone audit:

```json
{
  "text": "Draft a Mizar theorem proving 1 = 1."
}
```

Route with audit:

```json
{
  "query": "Draft a Mizar theorem proving 1 = 1.",
  "use_rag": true,
  "audit_neutrosophy": true
}
```

The audit returns `T`, `I_system_S`, `D_f`, `dF`, `F`, `i_fractal`, notes, and a conservative recommendation such as `draft_then_verify`, `verify_now`, `ask_clarifying_question`, or `inspect_mizar_errors`.

## Local development

The Docker path is the supported path. A local Python fallback still exists for development.

```bash
pip install -r requirements.txt
python src/app.py
```

## Repository notes

- `src/app.py` runs the Flask API
- `src/mizar_translator.py` turns verifier output into short educational feedback
- `src/ollama_proofreader.py` uses Ollama when available and falls back to heuristics
- `src/mizar_router.py` chooses the correct workflow before executing a tool
- `src/hipporag_service.py` wraps the optional HippoRAG backend
- `src/neutrosophic_auditor.py` produces optional operational T/I/F workflow audits
- `models/mizar-specialist/Modelfile` defines the Ollama Mizar-specialist behavior
- `mizar/` is a legacy Windows bundle kept for compatibility
- `UI/` is a legacy front-end sample kept for compatibility

## License

Apache-2.0. See [`LICENSE`](./LICENSE).
