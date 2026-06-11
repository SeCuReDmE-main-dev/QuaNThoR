# Survie Mizar (plan de stabilité)

## Objectif pédagogique

Rendre la vérification plus stable et plus rapide pour les étudiant·e·s,
et la correction plus prévisible pour les enseignants.

## Protocole minimal

1. **Article minimal d’abord**
   - `environ` + un seul `theorem` + `proof` + `end;`
2. **Une erreur → une correction**
   - corriger un point à la fois (ponctuation, vocabulaire, hypothèse, citation)
3. **Re-runs fréquents**
   - lancer `/verify` après chaque correction.
4. **Clôturer le niveau de validité**
   - seulement après `status=success` et `errors=[]`.

## Checklist étudiant

- [ ] L’article commence bien par `environ`.
- [ ] Les noms de notations / vocabulaires sont compatibles avec l’environnement chargé.
- [ ] Les `theorem`/`lemma` ont un but clair et un type attendu.
- [ ] Le bloc `proof` est présent et terminé par `end;`.
- [ ] Aucune phrase longue sans structure `proof` quand elle doit être prouvée.

## Checklist enseignant (TP, devoir, corrigé)

- [ ] Définir un cadre commun (`environ`) pour tous les devoirs.
- [ ] Interdire les modifications multiples sans recompilation intermédiaire.
- [ ] Demander un commentaire court `by`/`hence`/`thus` minimal quand la preuve est correcte.
- [ ] Utiliser `/route` pour uniformiser l’orientation des demandes :
  - brouillon vers les étudiants,
  - audit si la classe bute sur la formulation.
- [ ] Conserver une grille d’erreurs récurrentes pour la progression de la promo.

## Quand lancer l’audit et quel audit

- `POST /audit/neutrosophy` : quand la consigne est ambiguë ou incohérente avec la stratégie.
- `POST /audit/plithogenic-quaternion` : quand une version contextuelle RAG est utilisée.
- **Important** : aucun de ces audits ne remplace `/verify`.

## Commandes de survie (en pratique)

### Dépannage rapide (étudiant)

```powershell
curl -X POST http://localhost:5050/verify -H "Content-Type: application/json" --data-binary "@test.miz"
curl -X POST http://localhost:5050/route -H "Content-Type: application/json" --data "{\"text\":\"Je pense que le lemme manque un `by` ici.\",\"execute\":true}"
```

### Vérification de cohérence de cours

```powershell
curl -X POST http://localhost:5050/audit/neutrosophy -H "Content-Type: application/json" --data "{\"text\":\"Formalize a lemma about even numbers in Mizar.\"}"
```

## Chaîne opérationnelle à conserver

```text
I -> I_system^S -> D_f -> dF -> i_fractal
```

Cette chaîne est un **indicateur opérationnel**, pas une preuve mathématique.
