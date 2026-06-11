# Dépannage

## Le container ne démarre pas

- Vérifier Docker Desktop actif.
- Relancer :
  - `docker compose down`
  - `docker compose build --no-cache`
  - `docker compose up --build`
- Vérifier les logs : `docker logs quanthor`.

## `/health` indisponible

- Attendre la fin de l’initialisation (10-30s).
- Vérifier le port (par défaut `5050`).
- Vérifier la ligne `ports` dans `docker-compose.yml`.

## `mizar_available = false`

- Vérifier image et binaire Mizar dans le container.
- Refaire le build avec cache vidé.
- S’assurer que l’article envoyé à `/verify` contient bien :
  - `environ`
  - `begin`
  - `end;`

## Routeur bloqué (`needs_clarification`)

- Votre entrée n’est pas assez précise.
- Donner une forme claire :
  - si proposition formelle -> utiliser `code`
  - si question textuelle -> utiliser `text`/`query` et une phrase complète

## RAG indisponible

- `HIPPORAG_ENABLED` vaut `false` par défaut.
- Pour le mode sidecar, vérifier le profil `hipporag` et `HIPPORAG_SERVICE_URL`.

## Erreurs de syntaxe Mizar les plus fréquentes

- Point-virgule manquant.
- `proof` non fermé correctement.
- Importations manquantes dans `environ`.
- Article incomplet (pas de `end;`).

## Contrôle avant dépôt de travail

1. Lancer `curl http://localhost:5050/health`.
2. Lancer `test.miz` via `/verify`.
3. Corriger une erreur à la fois et revalider.
