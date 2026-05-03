"""
WSGI entrypoint for the SkillGap backend application.

This module constructs the Flask application by calling `create_app()` from
`backend/app/__init__.py`. The Flask development server is only started when
this file is executed directly.
"""

from app import create_app

# WSGI application object (used by local runs and compatible runners).
app = create_app()


if __name__ == "__main__":
    # Local development server only. Use gunicorn in production.
    app.run(debug=True, host="0.0.0.0", port=5000)
