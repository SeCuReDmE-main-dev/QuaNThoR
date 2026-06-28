# Installation et démarrage (Windows + container-first)

## 1. Ce que cette documentation suppose

- Docker Desktop installé.
- PowerShell (ou équivalent).
- Un terminal curl (inclut dans PowerShell récent).
- Un endpoint LLM optionnel pour la rédaction/routage. La route scolaire
  officielle reste Codex/OpenAI ou Antigravity/Gemini; Ollama n'est pas un
  fournisseur scolaire officiel.
  Sans endpoint LLM, la plupart des routes fonctionnent encore, avec fallback heuristique.

## 2. Installation recommandée (3 minutes)

### Lancement rapide (Windows)

Depuis `C:\Users\jeans\Desktop\book\QuaNThoR\QuaNThoR` :

```powershell
.\INSTALL_QUANTHOR.bat
.\START_QUANTHOR.bat
```

### Lancement direct container

```powershell
docker compose up --build
```

## 3. Point d’entrée par défaut

- Application : `http://localhost:5050`
- Interface web de test : `http://localhost:5050/`
- Santé : `http://localhost:5050/health`

## 4. Vérification immédiate (5 minutes)

1) Santé service

```powershell
curl http://localhost:5050/health
```

Conditions minimales attendues :
- `status` vaut `ok`
- `mizar_available` doit être `true` ou un diagnostic précis d’échec (mizar absent).

2) Vérification test de base

```powershell
curl -X POST http://localhost:5050/verify -H "Content-Type: application/json" --data-binary "@examples/mizar/minimal/test.miz"
```

3) Revalidation rapide

```powershell
curl http://localhost:5050/route -H "Content-Type: application/json" --data "{\"text\":\"Prove that 0 <= 0.\"}"
```

## 5. Variables d’environnement (minimal opérationnel)

Copier ces valeurs dans votre session ou `.env` (valeurs selon votre setup) :

```env
QUANTHOR_HOST_PORT=5050
MIZAR_TIMEOUT_SECONDS=60
# Variables historiques possibles pour compatibilité locale non officielle.
# Ne pas les présenter comme route scolaire officielle.
HIPPORAG_ENABLED=false
HIPPORAG_TOP_K=5
```

Notes de robustesse :

- Le proofreader public maintenu utilise le fallback local `school-heuristic`.
- Les anciennes variables de modèle sont compatibilité locale non officielle.
- Si une variable dédiée est vide, le code retombe sur la variable générique correspondante.

## 6. Configuration avancée (professeur / laboratoire)

### Mode RAG local (profil `hipporag`)

```powershell
$env:HIPPORAG_ENABLED = "true"
$env:HIPPORAG_SERVICE_URL = "http://hipporag:5100"
$env:HIPPORAG_LLM_BASE_URL = "http://host.docker.internal:11434/v1"
$env:HIPPORAG_EMBEDDING_BASE_URL = "http://host.docker.internal:11434/v1"
docker compose --profile hipporag up --build
```

### Mode Docker Docs (preview locale)

```powershell
docker compose --profile docs up docs
```

## 7. Construction de modèle Mizar dédié (recommandé)

1. Créer un modèle spécialisé :

```powershell
# Modèles locaux historiques: non officiels pour la route scolaire.
```

2. Forcer sa sélection :

```powershell
# Utiliser Codex/OpenAI ou Antigravity/Gemini pour la route scolaire maintenue.
```

## 8. Bonnes commandes d’exploitation

- `docker compose down` : arrêter proprement.
- `docker compose build --no-cache` : reconstruire complètement.
- `docker logs quanthor` : logs applicatifs.
- `python scripts/docgen.py check` : vérifier la cohérence docs auto.
- `python scripts/docgen.py build` : générer le site local de documentation.
