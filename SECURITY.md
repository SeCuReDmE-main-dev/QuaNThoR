# Politique de sécurité

QuaNThoR est un outil d’éducation et de vérification formelle.
Signalez toute vulnérabilité impactant le runtime container, l’API Flask ou
l’intégration proofreader local/HippoRAG.

## Contacter

- Email : `jeansebastienbeaulieuscrde.01@gmail.com`
- Sujet : `[SECURITY] QuaNThoR`

## Reproduction minimale demandée

1. Requête exacte (`curl`), headers inclus.
2. Payload complet.
3. Résultat attendu vs obtenu.
4. Étapes pour reproduire la panne.
5. Logs du conteneur si pertinent (`docker logs ...`).

## Zone couverte

- Entrées/sorties API `/verify`, `/route`, `/proofread`, `/draft`, `/rag/*`, `/audit/*`.
- Build et démarrage container.
- Intégration proofreader local et HippoRAG.

## Hors périmètre

- Demandes de fonctionnalités.
- Questions de support usage standard.
