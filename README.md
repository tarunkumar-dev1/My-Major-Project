# SkillGap AI Analyzer

Developer guide: how to run, test, and contribute to the project.

Prerequisites
- Python 3.9+ (recommended)
- pip
- (Optional) MongoDB server for integration tests — the app falls back to
	an in-memory `mongomock` instance if MongoDB is not available.

Setup
1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows
source .venv/bin/activate       # macOS / Linux
```

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. (Optional) Create a `.env` file in the `backend` folder to override
	 configuration values such as `MONGO_URI`, `JWT_SECRET`, and `GEMINI_API_KEY`.

Running the server (development)

```bash
cd backend
python app.py
```

This runs the Flask development server on `http://0.0.0.0:5000`.

Testing

Run the provided tests with pytest from the workspace root:

```bash
pytest -q
```

If a real MongoDB is unavailable tests will use the in-memory `mongomock` fallback.

Formatting & Static Analysis

- Apply Black formatting: `black .`
- Run flake8 linting: `flake8`

What I changed
- Added code-style configuration files (`pyproject.toml`, `.flake8`, `.editorconfig`).
- Expanded backend documentation with module and function docstrings.
- Added header comments to frontend assets and JS to improve readability.

Next suggested steps
- Add `pre-commit` hooks to enforce formatting on commit.
- Expand inline comments in any remaining complex modules (e.g., `ai_module`).
- Run full integration tests against a live MongoDB for production verification.

Deployment

Frontend on Vercel
- Deploy the repository root as a static site.
- `js/config.js` uses `/api` in production, so Vercel must proxy `/api/*` to the backend.
- Update `vercel.json` so the rewrite destination points to your Railway backend URL.

Backend on Railway
- Railway should use the repository root `requirements.txt` and `Procfile`.
- The backend entrypoint is `backend.wsgi:app`.
- Set environment variables such as `MONGO_URI`, `JWT_SECRET`, `FRONTEND_ORIGINS`, and `GEMINI_API_KEY` in Railway.

Local development
- Frontend pages load `js/config.js` and call `http://127.0.0.1:5000/api` automatically when served locally.
- Start the backend with `python backend/run_server.py`.

Contact
For questions about running or modifying the project, open an issue or contact the maintainer.
