# Deployment

## Topology

- Backend: FastAPI (uvicorn), port 8000
- Frontend: Vite build served statically or via dev server (5173)
- DB: SQLite file ./data/app.db (dev). Use Postgres in prod via DATABASE_URL.

## Run (dev)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env  # fill real values
uvicorn app.main:app --reload --port 8000

cd ../frontend
npm install
npm run dev
```

## Environment

All config via env vars (see .env.example). Never commit .env.

## Surgical update

```bash
docker compose up -d --no-deps backend
```

## Volumes

- ./data (SQLite DB) — persistent, never delete.
