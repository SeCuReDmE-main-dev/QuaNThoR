# QuaNThoR

QuaNThoR is a containerized Mizar verifier for students and mathematicians. It runs the official Linux Mizar package inside Docker and wraps the verifier output with a short explanation layer.

## What it does

- Verifies full `.miz` articles
- Returns raw verifier output and parsed errors
- Adds a short proof explanation in plain language
- Drafts a conservative Mizar skeleton from a natural-language request
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
- `MIZAR_TIMEOUT_SECONDS`: verifier timeout in seconds, default `60`
- `QUANTHOR_HOST_PORT`: host port exposed by Docker, default `5050`

If the configured model is not available, the backend falls back to the first compatible model it finds, preferring `gpt-oss:120b-cloud`, then math-focused and multilingual open models.

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
- `mizar/` is a legacy Windows bundle kept for compatibility
- `UI/` is a legacy front-end sample kept for compatibility

## License

Apache-2.0. See [`LICENSE`](./LICENSE).
