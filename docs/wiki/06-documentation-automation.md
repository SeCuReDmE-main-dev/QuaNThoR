# Documentation (maintenance produit)

Ce projet maintient un workflow de docs sans dépendance CI (pas de GitHub Action):

- Les pages manuelles (`docs/wiki/*.md`) décrivent l’usage réel.
- Les pages techniques (`docs/generated/*`) sont recalculées depuis le code via `scripts/docgen.py`.
- Le site est publié en local avec `mkdocs`.

## Standards de ce wiki

- Toute phrase d’usage doit refléter une route/variable qui existe réellement.
- Toute commande affichée doit être exécutable.
- Toute section "Résultat attendu" doit être testable par un curl minimal.

## Processus de production de docs

### 1) Modifier un fichier wiki

Éditer uniquement dans `docs/wiki/`.

### 2) Régénérer les pages auto

```powershell
python scripts/docgen.py generate
```

### 3) Vérifier l’alignement source → docs auto

```powershell
python scripts/docgen.py check
```

### 4) Compiler le site local

```powershell
python -m pip install -r requirements-docs.txt
python scripts/docgen.py build
```

### 5) Preuve visuelle

```powershell
python scripts/docgen.py serve --port 8000
```

## Référence de déploiement docs

- `docker compose --profile docs up docs`
- URL par défaut : `http://localhost:8000`

## Option GitBook (non bloquante)

Si l’équipe préfère une édition WYSIWYG, GitBook peut être utilisé en **édition**.
Le dépôt reste source de vérité technique, avec synchronisation manuelle vers GitBook :

1. Exporter le markdown `docs/wiki/*.md` et `docs/generated/*.md`.
2. Publier dans un espace GitBook existant.
3. Conserver ce dépôt comme vérité d’exécution pour les exemples d’API.
