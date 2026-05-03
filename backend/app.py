"""
WSGI entry for the Flask application.

This module exposes a WSGI `app` object which production servers (for example
gunicorn) can import using `gunicorn backend.app:app` or `gunicorn app:app`
depending on the working directory. Keep this file minimal — it should only
create the application and avoid side-effects.

Usage:
    - Development: `python backend/app.py` (runs Flask's dev server)
    - Production (gunicorn): `gunicorn backend.app:app --bind 0.0.0.0:$PORT`

Notes:
    - The factory function `create_app()` lives in `backend/app/__init__.py` and
        centralizes blueprint registration and extension initialization.
    - Do not import heavy modules at module import time to keep WSGI startup fast.
"""

from app import create_app

# Create the Flask WSGI application. This variable name (`app`) is what
# WSGI servers (gunicorn) will import, e.g. `gunicorn backend.app:app`.
app = create_app()


if __name__ == "__main__":
        # Development server: only use during local development and debugging.
        # The production deployment should use a WSGI server instead.
        app.run(debug=True, host='0.0.0.0', port=5000)
