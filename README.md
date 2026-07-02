<h1 align="center">QuaNThoR</h1>

![QuaNThoR Marketing Asset](assets/Marketing%20kit/(8).png)

<div align="center">

[![SecuredMe Education Suite public calendar](https://img.shields.io/badge/SecuredMe%20Education%20Suite-public%20calendar%20%7C%20alpha%20Aug%203%202026-5484ED?style=for-the-badge&logo=googlecalendar&logoColor=white)](https://calendrier.securedme.ca)

</div>

**Attribution:** Jean-Sebastien Beaulieu · [ORCID 0009-0007-2904-0443](https://orcid.org/0009-0007-2904-0443) · [SecuredMe](https://securedme.ca) · [QuaNThoR](https://quanthor.securedme.ca)

<!-- SECUREDME-SUITE-BADGES:START -->
[![Issues](https://img.shields.io/github/issues/SeCuReDmE-main-dev/QuaNThoR?color=161B6A)](https://github.com/SeCuReDmE-main-dev/QuaNThoR/issues)
[![Milestones](https://img.shields.io/badge/milestones-M0--M7-23B8FF)](https://github.com/SeCuReDmE-main-dev/QuaNThoR/milestones)
[![Project Board](https://img.shields.io/badge/project-kanban-6F42FF)](https://github.com/users/SeCuReDmE-main-dev/projects/3)
[![Branch](https://img.shields.io/badge/branch-PaQBoT-0E7490)](https://github.com/SeCuReDmE-main-dev/QuaNThoR/tree/PaQBoT)
<!-- SECUREDME-SUITE-BADGES:END -->

<!-- SECUREDME-STARTUP-SUPPORT:START -->
<p align="center">
  <a href="https://e2b.dev/startups">
    <img alt="Gateway-ready E2B audit lane" src="https://img.shields.io/badge/Gateway--ready-E2B%20audit%20lane-FF8800?style=for-the-badge" />
  </a>
  <a href="https://www.datadoghq.com/partner/datadog-for-startups/">
    <img alt="Gateway-ready Datadog observability" src="https://img.shields.io/badge/Gateway--ready-Datadog%20observability-632CA6?style=for-the-badge&amp;logo=datadog&amp;logoColor=white" />
  </a>
</p>

> **Gateway support acknowledgement.** This SecuredMe school tool is gateway-compatible. E2B audit support and Datadog observability are routed through the shared SecuredMe gateway when that lane is configured; this repository does not claim a direct E2B or Datadog runtime dependency by default, and no E2B or Datadog secret is stored in this README.
<!-- SECUREDME-STARTUP-SUPPORT:END -->




## School Authentication And Secret Boundary
This repository is a small SecuredMe school tool. Official classroom use must not require `.env` files, API keys, raw tokens, or local model secrets. Student and teacher workflows must use Codex/OpenAI or Antigravity/Gemini through browser WebAuth, fingerprinted session approval, and encrypted local session records when authentication is needed.

The reason for excluding generic local AI routes from official school mode is student and teacher safety: education accounts, provider-side account controls, browser login, and governed AI refusal behavior are safer than unguided local model endpoints for classroom cybersecurity and algorithm-building tools.

> **Development status.** This school tool is currently tagged **pre-alpha / in development**. External PRs are not evaluated for merge until the maintained tool reaches a stable, fully functional 100% classroom release after the pre-alpha phase. Issues and forks remain allowed, but official PR review is paused until that stability gate is met.

> **SecuredMe Education visual theme.** This pre-alpha school tool uses the shared SecuredMe Education open-source visual identity. See [assets/securedme/education](assets/securedme/education) for light/dark logo and thin banner assets.


> **Official school governance.** QuaNThoR is a supervised mathematics/proof education tool. The maintained classroom route supports Codex/OpenAI or Antigravity/Gemini only. See [SCHOOL_TOOL_GOVERNANCE.md](SCHOOL_TOOL_GOVERNANCE.md) and [AGENTS.md](AGENTS.md).

> **License.** This project uses the Secured Educational License 2.0 (SEL-2.0). It is provided for education, research, simulation, classroom training, and supervised learning. Misuse, unsafe private forks, unsupported provider routes, and unsupervised authority claims are not maintained or endorsed by the official school version. See [LICENSE](LICENSE), [NOTICE](NOTICE), [DISCLAIMER](DISCLAIMER), and [SAFETY.md](SAFETY.md).

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
2. Depuis `[local maintainer path redacted]` :

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

## License

This project is licensed under the Secured Educational License 2.0 (SEL-2.0). See [LICENSE](LICENSE).
---

![Mascotte Orion Vey](assets/mascot/Orion%20Vey%204.png)






