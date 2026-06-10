# QuaNThoR

QuaNThoR verifies Mizar articles and turns the verifier output into readable feedback.

The current runtime is container-first:

- Mizar runs inside Docker
- the container installs the official Linux Mizar 8.1.15 package
- explanations can use a remote Ollama server through `OLLAMA_BASE_URL`

## What this project is for

- Students can paste a proof and see where it fails
- Mathematicians can inspect raw verifier output and the cleaned-up explanation side by side
- Teachers can run the tool without a local Mizar installation on the host

## Quick Start

1. Install Docker Desktop.
2. Set `OLLAMA_BASE_URL` if you have a cloud Ollama endpoint.
3. Run `INSTALL_QUANTHOR.bat` to build the image.
4. Run `START_QUANTHOR.bat` to start the container.
5. Open `http://localhost:5000`.

## Environment Variables

- `OLLAMA_BASE_URL`: remote Ollama server root, for example `https://your-ollama.example.com`
- `OLLAMA_MODEL`: model name sent to Ollama, default `llama3.1`
- `MIZAR_TIMEOUT_SECONDS`: verifier timeout in seconds, default `60`

## API

### `GET /health`

Returns the active Mizar and Ollama runtime configuration.

### `POST /verify`

Request:

```json
{
  "code": "environ\n\nbegin\n\ntheorem T1: 1 = 1;\nproof\n  thus 1 = 1;\nend;\n\nend."
}
```

The response includes:

- `status`
- `errors`
- `raw_output`
- `ai_assistant`
- `dual_layer_verification`

## Local Development

The container path is the supported path. A local Windows fallback still exists for development, but it is secondary.

```bash
pip install -r requirements.txt
python src/app.py
```

## Repository Notes

- `src/app.py` runs the Flask API
- `src/mizar_translator.py` converts verifier output into educational language
- `src/google_proofreader.py` now uses Ollama when available
- `mizar/` is a legacy Windows bundle kept for compatibility
- `UI/` is a legacy front-end sample kept for compatibility

## License

See `LICENSE.md`.

