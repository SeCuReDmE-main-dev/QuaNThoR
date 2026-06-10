# QuaNThoR Repo Notes

- Supported runtime: Docker Compose on host port `5050`.
- Backend contract: `POST /verify` with JSON `{"code": "<full Mizar article>"}`.
- Health check: `GET /health`.
- Docker is the supported path. Local Python is only a development fallback.
- Keep docs short, concrete, and oriented to students and mathematicians.
- Use Apache-2.0 wording only. Do not revive the old SCL license flow.
- After runtime changes, validate with `docker compose build`, `docker compose up -d --force-recreate`, and a POST to `/verify` using `test.miz`.
