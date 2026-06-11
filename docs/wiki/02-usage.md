# Guide d’utilisation (étudiant, enseignant, correcteur)

## Principe de base

Chaque appel suit ce schéma :

1. Un étudiant/professeur soumet une intention (`text`, `query`, `prompt`, ou `code`).
2. `POST /route` classe l’intention :
   - vérification,
   - brouillon,
   - relecture,
   - clarification.
3. Selon le choix, l’outil exécute la bonne branche.

## 1) Vérifier un article Mizar

### Quand l’utiliser

- Quand vous avez un fichier `.miz` déjà structuré.

### Requête

```json
{
  "code": "environ ...\nbegin\n theorem T: 0 <= 1 by ...;\nproof\n...\nend;"
}
```

### Appel

```powershell
curl -X POST http://localhost:5050/verify -H "Content-Type: application/json" --data-binary "@examples/mizar/minimal/test.miz"
```

### Réponse attendue

- `status`: `success | failure | error`
- `return_code`: code retour du vérifieur Mizar
- `errors`: liste structurée (ou vide)
- `raw_output`: sortie brute Mizar
- `mizar_backend`: commande/exécutables utilisés
- `ai_assistant`: résumé pédagogique et amélioration de compréhension

## 2) Démarrer via le routeur unique

Utiliser pour tous les usages pédagogiques courants (recommandé).

```json
{
  "text": "Formalise: if n is even, then n+n is even.",
  "execute": true,
  "use_rag": false,
  "top_k": 5,
  "audit_neutrosophy": true,
  "audit_plithogenic_quaternion": false
}
```

```powershell
curl -X POST http://localhost:5050/route -H "Content-Type: application/json" --data "{\"text\":\"Formalise: if n is even, then n+n is even.\",\"execute\":true,\"audit_neutrosophy\":true}"
```

- `route` : branche décidée.
- `executed` : `true` si la branche a été lancée.
- `tool_result` : résultat concret de la branche.
- `neutrosophic_audit` : audit opérationnel optionnel.

## 3) Créer un brouillon Mizar

Quand la demande est textuelle :

```powershell
curl -X POST http://localhost:5050/draft -H "Content-Type: application/json" --data "{\"query\":\"Prove that the union of two finite sets is finite.\"}"
```

Réponse principale :
- `status`
- `mizar_draft`
- `ready_for_verifier`
- `assumptions`
- `clarifying_questions`
- `proof_strategy`

## 4) Améliorer la rédaction

Quand vous voulez améliorer des phrases d’explication :

```powershell
curl -X POST http://localhost:5050/proofread -H "Content-Type: application/json" --data "{\"text\":\"This theorem need prove with correct symbol.\"}"
```

Réponse :
- `improved_text`
- `suggestions`
- `grammar_score`
- `readability_score`
- `provider` (ollama | heuristic)

## 5) Audit opérationnel

- `POST /audit/neutrosophy` pour une note opérationnelle de cohérence.
- `POST /audit/plithogenic-quaternion` pour corrélation avec preuve + contexte.

Ces audits **ne remplacent pas** la validation `/verify`.

## 6) RAG (optionnel, seulement si activé)

Le bloc RAG ne sert pas à vérifier le formalisme Mizar ; il sert d’aide documentaire.

- `POST /rag/index` : indexe des documents.
- `POST /rag/retrieve` : extrait des passages.
- `POST /rag/qa` : question-réponse contextualisée.
- `GET /rag/status` : état RAG.

## 7) Séquence pédagogique recommandée

### Pour étudiants (environnement de TP)

1. Écrire l’énoncé en Mizar.
2. Lancer `/verify`.
3. Corriger **une erreur à la fois**.
4. Relancer `/verify`.
5. À chaque blocage, passer par `/route` + `/proofread` pour clarifier la formulation.

### Pour professeur (workflow de correction)

1. Donner un squelette article court.
2. Exiger une vérification à chaque modification.
3. Garder la piste `/health`, puis logs quand une erreur persiste.
4. Utiliser `needs_clarification` comme indicateur de consigne imprécise à renvoyer.
