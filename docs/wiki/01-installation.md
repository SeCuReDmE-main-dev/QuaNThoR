# Installation et démarrage

## 1) Prérequis

- Windows 10/11
- Docker Desktop
- (Optionnel) accès à un endpoint Ollama
- PowerShell

## 2) Installation minimale (recommandée)

```powershell
cd C:\Users\jeans\Desktop\book\QuaNThoR\QuaNThoR
.\INSTALL_QUANTHOR.bat
```

## 3) Démarrage

```powershell
.\START_QUANTHOR.bat
```

URL par défaut : `http://localhost:5050`.

## 4) Vérification de base

```powershell
curl http://localhost:5050/health
```

Contrôlez au moins : `mizar_available`, `mizar_command`, `status`.

## 5) `.env` utile

```env
QUANTHOR_HOST_PORT=5050
MIZAR_TIMEOUT_SECONDS=60
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_MIZAR_MODEL=qwen2.5:7b
OLLAMA_ROUTER_MODEL=mizar-specialist
HIPPORAG_ENABLED=false
HIPPORAG_TOP_K=5
```

## 6) Activation HippoRAG (optionnel)

```powershell
$env:HIPPORAG_ENABLED = "true"
$env:HIPPORAG_SERVICE_URL = "http://hipporag:5100"
$env:HIPPORAG_LLM_BASE_URL = "http://host.docker.internal:11434/v1"
$env:HIPPORAG_EMBEDDING_BASE_URL = "http://host.docker.internal:11434/v1"
docker compose --profile hipporag up --build
```

## 7) Références de reprise

- `docker-compose.yml` et `Dockerfile` : source de vérité runtime.
- `QUANTHOR_AUTODEBUG.ps1` : aide de diagnostique local.
