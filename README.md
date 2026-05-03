# SkillGap AI — Project Overview

This repository contains a simple student-facing skill gap analysis web application
with a Flask backend and a static frontend. The project is organized to support
separate deployments: the static frontend can be deployed to Vercel and the
Flask backend can be deployed to Railway or a similar host.

Quick structure

- `backend/` — Flask application and API (entrypoint: `backend/app.py`)
- `frontend/` — Static HTML/CSS/JS served as the site root for Vercel
- `data/`, `mongo_data/`, `mongo_data_clean/` — local Mongo/WiredTiger files (do not commit)

Local development

1. Backend (local):

```bash
# Create and activate your virtualenv, then from repo root:
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

The development server runs on `http://127.0.0.1:5000` by default. For production
use `gunicorn` and import the `app` WSGI object, e.g. `gunicorn backend.app:app`.

2. Frontend (static):

Serve the `frontend/` folder locally with a simple static server or open
`frontend/index.html` in your browser. The code expects the API to be available
at `/api` or `http://localhost:5000/api` during development.

Cleaning temporary files

- Temporary startup scripts and local mongod logs have been removed from the
  repository root. Use `.gitignore` to prevent local DB files from being
  committed. If you accidentally committed large `data/` or `mongo_data/`
  folders earlier, untrack them and then commit:

```bash
git rm -r --cached data mongo_data mongo_data_clean || true
git add -A
git commit -m "Remove local DB files from tracking and ignore them"
```

Commenting and documentation

- Key entrypoints (`backend/app.py`, `backend/run_server.py`, and
  `frontend/js/main.js`) now include explanatory comments and usage notes to
  help future maintainers.

Deployment notes

- Vercel: configure the project to serve `frontend/` as the site root (a
  `vercel.json` rewrite was added to map root paths to `frontend/$1`).
- Railway: ensure the service uses the `backend/Procfile` or place a
  `Procfile` at the repository root with `web: gunicorn backend.app:app --bind 0.0.0.0:$PORT`.

If you'd like, I can:

- Move the `Procfile` to the repo root and update it for Railway compatibility.
- Run the `git rm --cached` command to untrack the big DB folders and commit.
- Add more comments to other backend modules or generate an API README.

Contact

If you want me to proceed with any of the optional actions above, tell me
which and I'll apply the change and commit it.

Environment & Secrets (Important)

- Use `backend/.env.example` as the source of truth for required environment
  variables. Copy it to `backend/.env` for local development and fill the
  values. Never commit your `.env` file.
- The backend reads these variables at startup: `MONGO_URI`, `JWT_SECRET`,
  `GEMINI_API_KEY`, `AI_MODEL_NAME`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`.
- For production, set the same variables in your host (Railway, Vercel). Do
  not place API keys or secrets in frontend code — frontend must never contain
  long-lived secrets. Use environment variables on the server-side only.

Deploying (quick checklist)

- Vercel: Configure Environment Variables in the Project Settings. Ensure a
  rewrite or serverless function proxies `/api` to the backend if needed.
- Railway: Use the root `Procfile` included in this repo. Add environment
  variables via the Railway Dashboard's Environment section.

If you'd like, I can run the commands to untrack local DB folders and commit
the `.env.example` change for you.
