# Usage quotidien

## 1) Vérifier un article

Requête type :

```json
{
  "code": "environ ... begin ... theorem ... end;"
}
```

- Endpoint : `POST /verify`
- Réponse attendue : `status` + `errors` + `raw_output`.

## 2) Routeur unique

Envoyez une chaîne naturelle ou un article dans `query`/`text`/`prompt`/`code` :

```json
{ "query": "Prove that 1 = 1 in a minimal Mizar article." }
```

- Endpoint : `POST /route`
- Champs utiles :
  - `route` : branche choisie
  - `executed` : `true|false`
  - `tool_result` : résultat de la branche exécutée (si lancée)
  - `neutrosophic_audit` : optionnel

## 3) Drafting dédié

```json
{ "query": "Define a minimal theorem about even sums." }
```

- Endpoint : `POST /draft`
- Réponse : `mizar_draft`, `status`, `clarifying_questions`, `proof_strategy`.

## 4) Proofreading dédié

```json
{ "text": "show theorem of sum ..." }
```

- Endpoint : `POST /proofread`
- Réponse : `improved_text`, `suggestions`, `grammar_score`, `readability_score`.

## 5) RAG (si activé)

- `POST /rag/index` : ajoute du contexte.
- `POST /rag/retrieve` : recherche contextuelle.
- `POST /rag/qa` : réponse avec contexte.

## 6) Flux recommandé (cours/projets)

1. Formuler la demande.
2. Appeler `POST /route`.
3. Si `route=draft_mizar`, exécuter éventuellement `POST /verify`.
4. Corriger un point précis puis relancer `/verify`.
5. Répéter jusqu’à `status=success`.
