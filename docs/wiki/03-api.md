# Contrat API (référence exacte)

## Base

- URL de base : `http://localhost:5050`
- Format : JSON
- Encodage : UTF-8

## `GET /`

Retourne la page d’interface web du service.

---

## `GET /health`

### Objectif
Vérifier l’état global et les sous-systèmes.

### Réponse (exemple)

- `status`: `ok` ou `error`
- `mizar_available`: bool
- `mizar_share_dir`, `mizar_exec_dir`
- `ollama_base_url`
- `ollama_model_resolved`, `ollama_model_configured`
- `mizar_draft_structured_outputs` (booléen)
- `hipporag`: objet d’état HippoRAG
- `neutrosophic_audit_available`, `plithogenic_quaternion_audit_available`

---

## `POST /verify`

### Requête

```json
{ "code": "environ ... begin ... end;" }
```

### Champs requis
- `code` : chaîne (texte Mizar complet)

### Réponse
- `status` : `success | failure | error`
- `return_code` : code retour Mizar
- `errors` : liste d’erreurs structurées (`line`, `character`, `message`)
- `raw_output` : sortie brute Mizar
- `attempted_commands` : commande(s) essayées pour exécuter le vérifieur
- `mizar_backend` : détails du backend
- `ai_assistant` : analyse pédagogique (`human_explanation`, `suggestion`, etc.)

---

## `POST /route`

### Requête (contrat)

```json
{
  "text": "...",
  "context": "optionnel",
  "execute": true,
  "use_rag": false,
  "top_k": 5,
  "audit_neutrosophy": false,
  "audit_plithogenic_quaternion": false,
  "retrieval": []
}
```

- `query`, `prompt` ou `code` sont acceptés en plus de `text`.
- `execute` : exécuter la branche automatiquement (par défaut `true`).
- `use_rag` : ajouter du contexte RAG quand disponible.

### Réponse
- `status`: `routed` ou `needs_clarification`
- `route`: `proofread`, `draft_mizar`, `verify_mizar`, `needs_clarification`
- `executed`: booléen
- `decision`: objet de décision du routeur
- `tool_result`: résultat de la branche exécutée
- `neutrosophic_audit` : objet optionnel
- `plithogenic_quaternion_audit` : objet optionnel
- `clarifying_questions` : présent uniquement quand `route=needs_clarification`
- `http_status` : même code de la branche appelée (quand la branche `/verify` renvoie une erreur infra)

---

## `POST /draft`

### Requête

```json
{ "query": "formalize ...", "context": "optionnel" }
```

### Réponse
- `status` : `success | error`
- `mizar_draft`
- `assumptions`
- `clarifying_questions`
- `editing_suggestions`
- `proof_strategy`
- `ready_for_verifier`
- `confidence`

---

## `POST /proofread`

### Requête

```json
{ "text": "..." }
```

(`query`/`prompt` peuvent aussi être utilisés.)

### Réponse
- `status`: `success | error`
- `improved_text`
- `suggestions` (liste de corrections)
- `grammar_score`, `readability_score`
- `provider`

---

## `POST /audit/neutrosophy`

### Requête

- `text` ou `query` ou `prompt` ou `code`
- `context` optionnel
- `decision` optionnel (objet)
- `tool_result` optionnel
- `rag_context` / `rag_error` optionnels

### Réponse
- `scores` : `T`, `I_system_S`, `D_f`, `dF`, `F`, `i_fractal`
- `recommendation`
- `signals`
- `notes`
- `disclaimer`
- chaîne hiérarchique fixe : `I -> I_system^S -> D_f -> dF -> i_fractal`

---

## `POST /audit/plithogenic-quaternion`

### Requête

- `text` ou `query` ou `prompt` ou `code`
- `context` optionnel
- `retrieval`/`results`/`documents` optionnel
- `top_k` optionnel
- `neutrosophic_audit` optionnel

### Réponse
- `status`: `success`
- `audit_type`
- `scores` : `T`,`I_system_S`,`D_f`,`dF`,`F`,`i_fractal`
- `normalized_quaternion`
- `relations` + `hamilton_trace`
- `recommendation`

---

## `GET /rag/status`

État RAG (actif, désactivé, mode proxy, erreurs).

---

## `POST /rag/index`

Indexe des documents pour la recherche locale.

### Requête

- `docs`, `documents`, `text` : chaîne ou tableau de chaînes

### Réponse
- `status`, `indexed_documents`, `save_dir` ou erreur.

---

## `POST /rag/retrieve`

Recherche des fragments liés à une requête.

### Requête

```json
{ "query": "théorème de complétude", "top_k": 5 }
```

### Réponse
- `status`, `query`, `top_k`, `results`

---

## `POST /rag/qa`

Questions/réponses appuyées par RAG.

### Requête

```json
{ "query": "comment formaliser le théorème ...", "top_k": 5 }
```

### Réponse
- `status`, `query`, `top_k`, `results`

---

## Codes d’erreur usuels

- `400` : payload invalide ou vide
- `500` : erreur d’infra (Ollama/Mizar/HippoRAG indisponibles)
- `503` : problème optionnel de dépendance RAG au runtime
