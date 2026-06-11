# Documentation principale QuaNThoR

Ce wiki est la documentation officielle de consommation de **QuaNThoR**.

L’objectif : **installer vite, utiliser correctement, et diagnostiquer la vérification Mizar sans ambiguïté**, pour des profils étudiants et professeurs.

## Ce que fait l’application

- Vérifie des articles Mizar via le vérifieur (`/verify`) : `status success`, `failure` ou `error`.
- Sépare automatiquement la demande entrante avec `/route` :
  - `proofread`
  - `draft_mizar`
  - `verify_mizar`
  - `needs_clarification`
- Crée des brouillons Mizar lisibles depuis du texte naturel (`/draft`).
- Fait une correction de style/ponctuation orientée compréhension (`/proofread`).
- Propose des audits contextuels (neutrosophique + plithogénique quaternion) quand demandé.
- Intègre optionallement HippoRAG (`/rag/*`) pour ajouter du contexte.

## Démarrage de lecture

1. Commence par [01. Installation et démarrage](01-installation.md).
2. Vérifie la méthode d’usage dans [02. Guide d’utilisation](02-usage.md).
3. Lis le contrat API complet dans [03. Contrat API (consommation)](03-api.md).
4. Applique le workflow de dépannage dans [04. Dépannage opérationnel](04-troubleshooting.md).
5. Utilise les stratégies pédagogiques dans [05. Survie Mizar](05-mizar-survival.md).

## Références techniques annexes

- [Documentation générée automatiquement](../generated/documentation-summary.md)
- [Endpoints API auto-documentés](../generated/api-endpoints.md)
- [Variables d’environnement détectées](../generated/environment-variables.md)

## Convention de qualité de la documentation

- Aucune hypothèse fonctionnelle sans endpoint correspondant dans le code.
- Aucune commande non testée.
- Le champ "mémento" doit être court, utile, et reproductible.
