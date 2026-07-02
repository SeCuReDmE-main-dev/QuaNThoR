# Politique de sÃ©curitÃ©

## SecuredMe Education Governance Alignment

- Current phase: pre-alpha / in development.
- Repository license: Secured Educational License 2.0 (SEL-2.0), local metadata reference LicenseRef-SEL-2.0.
- Official AI-assisted classroom routes: Codex/OpenAI and Antigravity/Gemini only.
- Do not add Ollama Cloud, uncensored local AI, raw-token student flows, or unknown agent providers as official school routes.
- Preserve human-review boundaries; do not claim production, clinical, regulatory, enforcement, safety-critical, or autonomous authority readiness.
- Private modified copies, broken forks, and unreviewed rewrites are not a maintainer support obligation.


QuaNThoR est un outil dâ€™Ã©ducation et de vÃ©rification formelle.
Signalez toute vulnÃ©rabilitÃ© impactant le runtime container, lâ€™API Flask ou
lâ€™intÃ©gration proofreader local/HippoRAG.

## Contacter

- Contact: https://securedme.ca
- Sujet : `[SECURITY] QuaNThoR`

## Reproduction minimale demandÃ©e

1. RequÃªte exacte (`curl`), headers inclus.
2. Payload complet.
3. RÃ©sultat attendu vs obtenu.
4. Ã‰tapes pour reproduire la panne.
5. Logs du conteneur si pertinent (`docker logs ...`).

## Zone couverte

- EntrÃ©es/sorties API `/verify`, `/route`, `/proofread`, `/draft`, `/rag/*`, `/audit/*`.
- Build et dÃ©marrage container.
- IntÃ©gration proofreader local et HippoRAG.

## Hors pÃ©rimÃ¨tre

- Demandes de fonctionnalitÃ©s.
- Questions de support usage standard.
