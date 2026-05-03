"""
Standalone server runner for local environments.

This script ensures the `backend` package path is importable and starts the
Flask app with environment-configurable host/port values.
"""

import os
import sys

# Ensure backend/ is importable when running this file directly.
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app


def main():
    """Create and run the Flask development server."""
    app = create_app()
    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000"))
    )


if __name__ == "__main__":
    main()
