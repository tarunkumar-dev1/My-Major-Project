"""
WSGI entrypoint for the SkillGap backend application.

This module constructs the Flask application by calling `create_app()` from
the `app` package and provides a simple `__main__` runner for local
development. The `app.run` call is only executed when this file is run as a
script (not when imported by a WSGI server).

Usage:
    python backend/app.py

Note: For production deployments, use a WSGI server (gunicorn, uWSGI, etc.)
and do not rely on the Flask development server provided here.
"""

from app import create_app


# Create the Flask application instance using the factory in `app.__init__`.
app = create_app()


if __name__ == "__main__":
    # The built-in Flask server is suitable for local development and
    # debugging only. Keep `debug=True` during active development to enable
    # the auto-reloader and useful debug information — remember to turn it
    # off for production.
    app.run(debug=True, host='0.0.0.0', port=5000)
