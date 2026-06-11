# QuaNThoR

## À quoi sert cet outil

`QuaNThoR` est un assistant de vérification Mizar orienté **étudiants** et **mathématiciens**.

Ce que le service fait réellement :

- Vérifie des articles Mizar complets (`.miz`) via le vérifieur Mizar.
- Route automatiquement une demande entre :
  - `proofread`
  - `draft_mizar`
  - `verify_mizar`
  - `needs_clarification`
- Produit un brouillon Mizar depuis une demande en langage naturel.
- Propose une correction grammaticale/punctuationnelle (via Ollama).
- Expose des aides de flux (RAG HippoRAG, audit neutrosophique) optionnelles.

Toutes les exécutions lourdes (vérifieur, génération) tournent dans Docker.  
Le dépôt est prévu en mode **container-first**.

## Démarrage rapide (Windows)

1. Avoir Docker Desktop installé.
2. Depuis `C:\Users\jeans\Desktop\book\QuaNThoR\QuaNThoR` :

```powershell
.\INSTALL_QUANTHOR.bat
.\START_QUANTHOR.bat
```

3. Ouvrir `http://localhost:5050`.

Alternative directe :

```powershell
docker compose up --build
```

## Fonctions utiles (endpoints)

### `GET /health`

- Vérifie la disponibilité des briques (Mizar, Ollama, HippoRAG, audit).
- Réponse attendue : JSON avec `status: "ok"`.

### `POST /verify`

- Corps JSON : `{ "code": "environ ... theorem ... end;" }`
- `code` doit être un article Mizar complet (`environ`, `begin`, `end;`).
- Réponses principales :
  - `status`: `success | failure | error`
  - `errors`: liste structurée d’erreurs détectées
  - `raw_output`: sortie brute du vérifieur

### `POST /route`

- Corps JSON : `text` OU `query` OU `prompt` OU `code`
- Retourne un `route` puis, si `execute: true`, exécute la branche choisie.
- Champs utiles : `route`, `executed`, `tool_result`, `neutrosophic_audit` (optionnel).

### `POST /draft`

- Corps JSON : `{ "query": "..." }`
- Produit un brouillon Mizar conservatif : `status`, `mizar_draft`, questions de clarification.

### `POST /proofread`

- Corps JSON : `{ "text": "..." }`
- Retourne un texte amélioré + suggestions.

### `POST /audit/neutrosophy`

- Corps JSON : `text | query | prompt | code`
- Retour : chaîne d’audit opérationnel (`T`, `I_system_S`, `D_f`, `dF`, `F`, `i_fractal`) et recommandation.
- La chaîne officielle reste :

```text
I -> I_system^S -> D_f -> dF -> i_fractal
```

### RAG (optionnel)

- `GET /rag/status`
- `POST /rag/index`
- `POST /rag/retrieve`
- `POST /rag/qa`

## Variables d’environnement utiles

- `OLLAMA_BASE_URL` : endpoint Ollama (par défaut `http://host.docker.internal:11434` en container)
- `OLLAMA_MODEL` : modèle de secours pour proofreading
- `OLLAMA_MIZAR_MODEL` : modèle brouillon Mizar
- `OLLAMA_ROUTER_MODEL` : modèle de routeur
- `OLLAMA_MIZAR_BASE_URL` : endpoint dédié au drafting si différent
- `MIZAR_TIMEOUT_SECONDS` : timeout vérifieur (par défaut `60`)
- `HIPPORAG_ENABLED` : `true|false` (défaut `false`)
- `HIPPORAG_SERVICE_URL` : URL du sidecar, ex. `http://hipporag:5100`
- `HIPPORAG_LLM_BASE_URL` / `HIPPORAG_EMBEDDING_BASE_URL`
- `HIPPORAG_LLM_MODEL` / `HIPPORAG_EMBEDDING_MODEL`
- `HIPPORAG_TOP_K` : nombre de résultats
- `QUANTHOR_HOST_PORT` : port hôte de l’API (défaut `5050`)

## Exemples d’usage minimal

```powershell
curl http://localhost:5050/health

curl -X POST http://localhost:5050/verify -H "Content-Type: application/json" --data-binary "@test.miz"

curl -X POST http://localhost:5050/route -H "Content-Type: application/json" --data "{\"text\":\"Prove a minimal theorem about even numbers.\"}"
```

## Profils recommandés

- Sans RAG (recommandé) : `docker compose up --build`
- Avec RAG local (expérimental) :

```powershell
$env:HIPPORAG_ENABLED = "true"
$env:HIPPORAG_SERVICE_URL = "http://hipporag:5100"
$env:HIPPORAG_LLM_BASE_URL = "http://host.docker.internal:11434/v1"
$env:HIPPORAG_EMBEDDING_BASE_URL = "http://host.docker.internal:11434/v1"
docker compose --profile hipporag up --build
```

## Modèle spécialisé Mizar (recommandé)

1. Construire le modèle :

```powershell
ollama create mizar-specialist -f .\models\mizar-specialist\Modelfile
```

2. Forcer son usage :

```powershell
$env:OLLAMA_ROUTER_MODEL = "mizar-specialist"
$env:OLLAMA_MIZAR_MODEL = "mizar-specialist"
```

## Références internes du dépôt

- `src/app.py` : API Flask
- `src/mizar_router.py` : logique de route
- `src/mizar_drafter.py` : brouillon Mizar
- `src/mizar_translator.py` : explicitation pédagogique
- `src/ollama_proofreader.py` : correction grammaticale/punctuation
- `src/hipporag_service.py` / `src/hipporag_api.py` : couche RAG
- `models/mizar-specialist/Modelfile` : prompt de modèle
- `docs/wiki/*` : mode d’emploi détaillé
- `SECURITY.md`, `LICENSE` : règles de sécurité / licence

## Licence

Apache-2.0 (`LICENSE`).
