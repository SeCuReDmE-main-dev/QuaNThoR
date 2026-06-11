# Contrat API

## Base

- URL locale : `http://localhost:5050`

## `GET /health`

- Contrôle de santé.
- Retour : statut global + disponibilité des briques.

## `POST /verify`

Corps :

```json
{ "code": "environ ... begin ... end;" }
```

Réponse (principale) :

- `status`: `success` | `failure` | `error`
- `errors`: liste d’erreurs structurées
- `raw_output`: sortie brute
- `ai_assistant`: interprétation pédagogique

## `POST /route`

Corps :

```json
{
  "query": "Draft a minimal theorem.",
  "use_rag": false,
  "audit_neutrosophy": true
}
```

Réponse :

- `route`: `proofread | draft_mizar | verify_mizar | needs_clarification`
- `executed`: booléen
- `tool_result`: résultat de la branche exécutée
- `neutrosophic_audit`: optionnel

## `POST /draft`

Corps : `{ "query": "..." }`  
Réponse : `mizar_draft`, `status`, `ready_for_verifier`, `assumptions`.

## `POST /proofread`

Corps : `{ "text": "..." }`  
Réponse : `improved_text`, `suggestions`, `readability_score`.

## `POST /audit/neutrosophy`

Corps : `text` ou `query` ou `prompt` ou `code`  
Réponse : `T`, `I_system_S`, `D_f`, `dF`, `F`, `i_fractal`, `recommendation`.

## Endpoints RAG

- `GET /rag/status`
- `POST /rag/index`
- `POST /rag/retrieve`
- `POST /rag/qa`
