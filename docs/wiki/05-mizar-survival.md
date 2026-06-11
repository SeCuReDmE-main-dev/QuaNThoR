# Mode survie Mizar

## Protocole étudiant

1. Soumettre un article complet.
2. Exécuter `/verify`.
3. Corriger **une erreur**.
4. Réexécuter `/verify`.
5. Répéter jusqu’à `status=success`.

## Pour les professeurs

- Standardiser un squelette minimal dans les consignes :
  - `environ` explicite
  - imports de `vocabularies`, `notations`, `constructors`, `theorems`
- Vérifier la structure pédagogique avant la complexité :
  - `theorem`
  - `proof`
  - `end;`

## Erreurs récurrentes

- `environ` incomplet
- `end;` manquant
- `theorem` sans `proof`
- hypothèses insuffisamment précisées

## Quand déclencher l’audit

- Avant un draft long
- Lorsque la sortie route est ambiguë
- Comme signal de prudence, jamais comme preuve logique

## Chaîne opérationnelle à conserver

```text
I -> I_system^S -> D_f -> dF -> i_fractal
```
