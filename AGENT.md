# Notes opérationnelles QuaNThoR

- Runtime de production : **Docker Compose**, port hôte par défaut `5050`.
- Contrat API principal :
  - `POST /verify` avec `{"code": "<article Mizar complet>"}`.
  - `GET /health` expose l’état `Mizar`, `Ollama`, `HippoRAG`, audit.
- Référence d’exécution principale : `Dockerfile` + `docker-compose.yml`.
- Exécution Python locale : uniquement pour debug/développement.
- Documentation attendue : concise, orientée usage réel, adaptée étudiants/mathématiciens.
- Licence : **Apache-2.0 uniquement**.
- Vérification fonctionnelle minimale après changement infra :
  - `docker compose build`
  - `docker compose up --build`
  - `curl -X POST http://localhost:5050/verify -H "Content-Type: application/json" --data-binary "@test.miz"`.
- Ne pas documenter ni utiliser le workflow de verrouillage obsolète.
