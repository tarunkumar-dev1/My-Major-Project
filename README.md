# SkillGap AI Analyzer

Developer guide for running, testing, and deploying the project.

## Project Structure

- `frontend/`: static HTML/CSS/JS files
- `backend/`: Flask API application
- `vercel.json`: frontend deployment/rewrite config for Vercel
- `Procfile`: backend process command for Railway

## Prerequisites

- Python 3.9+
- pip
- Optional: MongoDB (the app can fall back to `mongomock` for local use)

## Local Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

2. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Create local environment file:

```bash
copy backend\.env.example backend\.env
```

4. Fill `backend/.env` values:

- `MONGO_URI`
- `JWT_SECRET`
- `GROQ_API_KEY`
- `AI_MODEL_NAME`
- `FRONTEND_ORIGINS`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

5. Run backend:

```bash
python backend/run_server.py
```

Backend runs on `http://0.0.0.0:5000` by default.

## Frontend Behavior

- `frontend/js/config.js` chooses API base URL:
    - local: `http://127.0.0.1:5000/api`
    - deployed: `/api`

## Deployment

### Frontend on Vercel

- Deploy repository root.
- Ensure `vercel.json` is configured.
- Replace the placeholder Railway backend URL in `vercel.json` rewrite destination.

### Backend on Railway

- Use root `Procfile` (`web: gunicorn backend.wsgi:app --bind 0.0.0.0:$PORT`).
- Set required environment variables in Railway dashboard.

## Security Notes

- Never commit real secrets in `.env`.
- Do not store API keys in frontend files.
- Change default/admin credentials before production use.

## Testing

Run tests from repository root:

```bash
pytest -q
```
