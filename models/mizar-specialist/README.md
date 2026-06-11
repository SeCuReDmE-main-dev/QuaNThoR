# Mizar Specialist Modelfile

Create the specialist model with:

```powershell
ollama create mizar-specialist -f .\models\mizar-specialist\Modelfile
```

Then run QuaNThoR with:

```powershell
$env:OLLAMA_ROUTER_MODEL = "mizar-specialist"
$env:OLLAMA_MIZAR_MODEL = "mizar-specialist"
docker compose up --build
```

The default `Modelfile` is usable immediately as a prompt-specialized Mizar router/drafter. After training a LoRA or QLoRA adapter on Mizar examples, add an `ADAPTER` line that points to the adapter directory:

```text
ADAPTER C:\path\to\mizar-lora-adapter
```

The adapter must be trained from the same base model named in `FROM`.
