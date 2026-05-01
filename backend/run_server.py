"""
Standalone server runner for local environments.

This script provides a small wrapper to start the Flask application on
`127.0.0.1:5000`. It manipulates `sys.path` so the `app` package within the
`backend` directory can be imported when running this file directly. For
production deployments prefer a WSGI server instead of this helper.
"""

import sys
import os

# Ensure the current package (backend/) is importable when running this file
# directly. This allows `from app import create_app` to succeed.
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app


# Create and run the Flask app. The host/port follow Railway-friendly defaults
# so this runner behaves like production when `PORT` is provided.
app = create_app()
app.run(
	debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
	host=os.getenv('HOST', '0.0.0.0'),
	port=int(os.getenv('PORT', '5000'))
)
