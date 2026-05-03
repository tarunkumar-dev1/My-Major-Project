"""
Local run helper for the Flask application.

This script exists to make it convenient to start the app in a local
development environment in environments where importing from the package
root may not be configured. It ensures `backend` is on the import path and
starts the Flask app using the built-in server.

Do not use this script in production. Use a WSGI server (gunicorn) that
imports the `app` object from `backend.app` instead.
"""

import sys
import os

# Ensure the package directory is on sys.path so `from app import create_app`
# works even when this script is executed directly from the backend folder.
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app


def main():
		"""Create and run the Flask development server.

		- Debug is set to False here to match a simple local run; set to True
			if you need the debugger and auto-reload locally.
		- Host is bound to 127.0.0.1 to avoid exposing the dev server publicly.
		"""
		app = create_app()
		app.run(debug=False, host='127.0.0.1', port=5000)


if __name__ == '__main__':
		main()
