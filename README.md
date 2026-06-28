# QuaNThoR

## School Authentication And Secret Boundary
This repository is a small SecuredMe school tool. Official classroom use must not require `.env` files, API keys, raw tokens, or local model secrets. Student and teacher workflows must use Codex/OpenAI or Antigravity/Gemini through browser WebAuth, fingerprinted session approval, and encrypted local session records when authentication is needed.

The reason for excluding generic local AI routes from official school mode is student and teacher safety: education accounts, provider-side account controls, browser login, and governed AI refusal behavior are safer than unguided local model endpoints for classroom cybersecurity and algorithm-building tools.

> **Development status.** This school tool is currently tagged **pre-alpha / in development**. External PRs are not evaluated for merge until the maintained tool reaches a stable, fully functional 100% classroom release after the pre-alpha phase. Issues and forks remain allowed, but official PR review is paused until that stability gate is met.

> **SecuredMe Education visual theme.** This pre-alpha school tool uses the shared SecuredMe Education open-source visual identity. See [assets/securedme/education](assets/securedme/education) for light/dark logo and thin banner assets.


> **Official school governance.** QuaNThoR is a supervised mathematics/proof education tool. The maintained classroom route supports Codex/OpenAI or Antigravity/Gemini only. See [SCHOOL_TOOL_GOVERNANCE.md](SCHOOL_TOOL_GOVERNANCE.md) and [AGENTS.md](AGENTS.md).

> **Notice and disclaimer.** The existing Apache-2.0 project license remains active. See [NOTICE](NOTICE) and [DISCLAIMER](DISCLAIMER) for attribution, school-governance, and misuse-responsibility boundaries.

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
- Propose une correction grammaticale/punctuationnelle locale et conservative.
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

- Vérifie la disponibilité des briques (Mizar, proofreader local, HippoRAG, audit).
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

- Les variables `SCHOOL_LLM_*` configurent le runtime modèle provider-neutre.
- Les variables historiques `OLLAMA_*` peuvent encore exister pour compatibilité
  locale, mais elles ne sont pas la route scolaire officielle.
- La route officielle de correction publique utilise le proofreader local
  `school-heuristic`.
- `MIZAR_TIMEOUT_SECONDS` : timeout vérifieur (défaut `60`).
- `HIPPORAG_ENABLED` : `true|false` (défaut `false`)
- `HIPPORAG_SERVICE_URL` : URL du sidecar, ex. `http://hipporag:5100`
- `HIPPORAG_LLM_BASE_URL` / `HIPPORAG_EMBEDDING_BASE_URL`
- `HIPPORAG_LLM_MODEL` / `HIPPORAG_EMBEDDING_MODEL`
- `HIPPORAG_TOP_K` : nombre de résultats
- `QUANTHOR_HOST_PORT` : port hôte de l’API (défaut `5050`)

## Exemples d’usage minimal

```powershell
curl http://localhost:5050/health

curl -X POST http://localhost:5050/verify -H "Content-Type: application/json" --data-binary "@examples/mizar/minimal/test.miz"

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

## Modèle spécialisé Mizar

Le dossier `models/` peut contenir du matériel expérimental ou historique. Il ne
définit pas une route scolaire officielle. Pour les usages de classe maintenus,
utiliser la vérification Mizar, le proofreader local, Codex/OpenAI ou
Antigravity/Gemini selon la gouvernance scolaire du dépôt.

## Références internes du dépôt

- `src/app.py` : API Flask
- `src/mizar_router.py` : logique de route
- `src/mizar_drafter.py` : brouillon Mizar
- `src/mizar_translator.py` : explicitation pédagogique
- `src/school_proofreader.py` : correction grammaticale/punctuation locale
- `src/school_model_runtime.py` : helper provider-neutre pour les usages modèle
- `src/ollama_proofreader.py` : compatibilité historique non officielle
- `src/hipporag_service.py` / `src/hipporag_api.py` : couche RAG
- `models/mizar-specialist/Modelfile` : prompt de modèle
- `examples/mizar/minimal/test.miz` : fixture Mizar minimale
- `docs/wiki/*` : mode d’emploi détaillé
- `SECURITY.md`, `LICENSE` : règles de sécurité / licence

## Documentation automatique (sans GitHub Action)

### Solution choisie pour être 100% opérationnelle

- Flux local primaire (sans GitHub Action) : **MkDocs Material + génération locale** (`scripts/docgen.py`).
- Option éditeur : **GitBook** si vous voulez une édition SaaS collaborative.
- Aucun pipeline GitHub Action requis dans ce dépôt.

### Commandes utiles

```powershell
python scripts/docgen.py generate       # Génère la docs auto dans docs/generated/*
python scripts/docgen.py check           # Vérifie la synchronisation docs auto
python -m pip install -r requirements-docs.txt
python scripts/docgen.py build           # Build du site local
python scripts/docgen.py serve --port 8000 # Prévisualisation locale
docker compose --profile docs up docs    # Prévisualisation locale en container MkDocs
```

### To-Do de la facette docs

- [x] Workflow local gratuit actif (`scripts/docgen.py` + MkDocs).
- [x] Vérification de dérive docs auto via `python scripts/docgen.py check`.
- [x] Prévisualisation locale via `python scripts/docgen.py serve --port 8000` ou `docker compose --profile docs up docs`.
- [ ] Ajouter un "docs check" obligatoire avant tout release locale.

## Public Archive Intent

QuaNThoR est destiné à être publié comme outil public gratuit pour l’apprentissage, l’expérimentation et la vérification formelle. Il n’est pas destiné à être vendu ou transformé en produit commercial fermé.

Le dépôt doit rester utilisable sans dépendance obligatoire à une API propriétaire. Certaines intégrations peuvent être optionnelles, mais le coeur de l’outil et ses exemples doivent rester accessibles publiquement.

Après la présentation finale, le dépôt sera archivé dans l’état livré. Aucune maintenance continue, refonte, support commercial ou roadmap post-archive n’est promise. Les personnes qui souhaitent l’utiliser devront le trouver, le lire et l’exécuter tel quel.

## Licence

Apache-2.0 (`LICENSE`).



