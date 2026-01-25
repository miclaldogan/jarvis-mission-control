# jarvis-mission-control client (Vite)

This folder contains the active React UI.

## Recommended: run via Docker (HMR)

From repo root:

```bash
docker compose --profile dev up -d --build backend redis frontend-dev
```

- UI: `http://localhost:5173`
- API proxy (from UI): `http://localhost:5173/api/...` (forwards to backend)

Stop:

```bash
docker compose --profile dev down
```

## Local run (Node)

Requirements: Node.js 18+ (Node 20 recommended).

If you use `nvm`, from repo root you can run:

```bash
nvm use
```

```bash
cd client
npm install
npm run dev
```

### API base URL

In development we rely on the Vite dev proxy (`/api`), so you usually don't need `VITE_API_BASE_URL`.

If you want to point the dev proxy to a different backend:

```bash
VITE_DEV_PROXY_TARGET=http://localhost:8000 npm run dev
```

## Production UI (nginx)
When running the production UI container (`http://localhost:3000`), the frontend uses same-origin calls:
- `/api/*` is proxied to the backend
- `/metrics` and `/health` are also proxied to the backend
