# Dépannage opérationnel (runbook)

## 1) Lancement et santé

### Symptôme : impossible d’atteindre `http://localhost:5050/health`

1. `docker ps` : vérifier le container `quanthor` ou `quanthor_quanthor` selon votre compose.
2. `docker logs quanthor` : lire le message d’init.
3. Forcer un démarrage propre :

```powershell
docker compose down
docker compose build --no-cache
docker compose up --build
```

4. Attendre la fin du bootstrap (~10-30 s) puis retenter.

### Symptôme : service up, mais port indisponible

- Contrôler `QUANTHOR_HOST_PORT`.
- Vérifier qu’aucun autre service n’écoute déjà sur ce port.
- Relancer avec `-p 0.0.0.0:5050:5000` si nécessaire depuis la config.

## 2) `/verify` retourne `mizar_available: false` ou erreur de commande

1. Vérifier qu’un vrai article est envoyé (`environ`, `begin`, `theorem`, `proof`, `end;`).
2. Contrôler que le conteneur a été reconstruit avec un Mizar téléchargé/valide.
3. Relancer avec cache vidé :

```powershell
docker compose build --no-cache quanthor
docker compose up quanthor
```

4. Vérifier `mizar_share_dir` et `mizar_exec_dir` via `/health`.

## 3) Routeur mal classé

### Symptôme : `route = needs_clarification`

- Donner un input plus précis :
  - demande mathématique précise => `code` ou texte avec `theorem`, `lemma`, `proof`.
  - demande textuelle => phrase complète et explicite en `text`.

### Symptôme : route incorrecte mais exécution bloquée

- Utiliser le même appel avec `execute: false` :

```powershell
curl -X POST http://localhost:5050/route -H "Content-Type: application/json" --data "{\"text\":\"...\",\"execute\":false}"
```

- Si la décision est cohérente, relancer avec `execute: true`.

## 4) Erreurs Mizar classiques

- `end;` manquant.
- `proof` non fermé / bloc non équilibré.
- Imports absents (`environ` incomplet).
- Théorème sans hypothèses suffisantes.
- Séquence de tokens incorrecte (`then`, `assume`, `thus` mal placés).

## 5) RAG désactivé ou indisponible

`HIPPORAG_ENABLED` vaut `false` par défaut. Deux modes :

- **In-process** : `HIPPORAG_ENABLED=true` et package `hipporag` disponible.
- **Proxy** : `HIPPORAG_SERVICE_URL` pointant vers un service externe.

Vérifier :

```powershell
curl http://localhost:5050/rag/status
```

Puis, si proxy requis :

```powershell
docker compose --profile hipporag up --build
```

## 6) Checklist avant livraison d’un lot d’exercices

1. `curl http://localhost:5050/health`
2. `examples/mizar/minimal/test.miz` via `/verify`
3. Une demande `curl /route` minimale
4. Aucun appel critique en mode `execute: true` sans confirmation visuelle de la santé
5. Logs de container propres pour les erreurs non déterministes

## 7) Escalade support

Quand une erreur persiste :
- exporter: request JSON, response JSON, logs et horaire.
- noter la version du conteneur.
- ouvrir une issue avec reproduction minimale (fichier `.miz`, commande exacte, output).
