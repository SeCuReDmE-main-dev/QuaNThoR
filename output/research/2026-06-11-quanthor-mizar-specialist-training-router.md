# Objective
Define the best practical way to make QuaNThoR Mizar-specialist with Ollama, and put a controller in charge of routing text separation, proofreading, drafting, and verification.

# Environment / Stack Context
- Repo: `C:\Users\jeans\Desktop\book\QuaNThoR\QuaNThoR`
- Runtime: Flask API in Docker, containerized Mizar verifier, Ollama on the host or remote
- Current behavior: the repo already has separate proofreader and drafter helpers, plus `/verify` and `/draft`
- Ollama current constraint: cloud models are usable, but cloud structured outputs are not supported

# Research Questions
- Should Ollama itself be trained, or should a fine-tuned adapter be imported into Ollama?
- Which base model family is the safest fit for a Mizar-specialist adapter?
- How should the app decide whether a request needs proofreading, Mizar drafting, verification, or clarification?
- Should the model execute the tools directly, or should the server keep execution control?

# Findings
- **Confirmed by primary sources:** Ollama does not provide a training loop inside Ollama; the documented path is to fine-tune elsewhere and import the result with a `Modelfile` using `FROM` plus `ADAPTER`.
- **Confirmed by primary sources:** Ollama’s adapter import docs list supported adapter architectures as Llama, Mistral, and Gemma. The import docs for full models also list Llama, Mistral, Gemma, and Phi3.
- **Confirmed by primary sources:** The `Modelfile` can set `SYSTEM`, `PARAMETER`, `TEMPLATE`, `MESSAGE`, and `ADAPTER`, which is enough to build a specialist behavior layer around a fine-tuned base model.
- **Confirmed by primary sources:** Ollama supports tool calling, which is the right mechanism for letting a model decide which tool to invoke while the server performs the actual execution.
- **Confirmed by primary sources:** Ollama Cloud does not support structured outputs, so any cloud-backed router must fall back to prompt-only JSON parsing.
- **Confirmed by primary sources:** Mizar 8.1.15 is the current official version, and the syntax docs still describe the classic article structure `environ ... begin ... end`.
- **Inferred from the docs:** If the goal is a trainable Ollama-compatible specialist, the safest base family is `mistral` or `llama3.1`, not a cloud-only workflow.
- **Inferred from the repo:** QuaNThoR already separates responsibilities well enough to add a router without rewriting the verifier or the proofreader.

# Recommended Path
1. Keep Mizar as the only verifier of mathematical correctness.
2. Fine-tune a supported base model outside Ollama with LoRA or QLoRA, then import the adapter into Ollama.
3. Use a dataset of paired examples:
   - natural language request -> Mizar skeleton
   - raw verifier error -> corrective explanation
   - prose explanation -> proofread version
   - ambiguous request -> clarifying questions
4. Build a small server-side router that classifies each request into:
   - `proofread`
   - `draft_mizar`
   - `verify_mizar`
   - `needs_clarification`
5. Let the model recommend the route, but keep tool execution on the server.
6. Use tool calling or structured JSON for the router, and keep prompt-only JSON fallback for cloud models.

# Alternatives Considered
- Training directly inside Ollama: not the documented path.
- Using `gpt-oss:120b-cloud` as the final specialist base: good for inference, but not the best choice for a custom adapter workflow.
- Relying only on prompt engineering: useful as a first pass, but weaker than a real adapter for repeated Mizar tasks.

# Risks / Unknowns
- Adapter quality depends on the dataset quality more than on the base model choice.
- Mizar examples need careful normalization so the model learns structure, not accidental syntax noise.
- Cloud-backed models may change availability and cannot rely on structured outputs.
- A router that is too aggressive can hide ambiguity instead of asking the user for clarification.

# Sources
- Ollama import docs: https://docs.ollama.com/import
- Ollama Modelfile reference: https://docs.ollama.com/modelfile
- Ollama structured outputs: https://docs.ollama.com/capabilities/structured-outputs
- Ollama tool calling: https://docs.ollama.com/capabilities/tool-calling
- Ollama cloud docs: https://docs.ollama.com/cloud
- Mizar home page: https://mizar.uwb.edu.pl/
- Mizar syntax reference: https://mizar.uwb.edu.pl/version/current/doc/syntax.txt
