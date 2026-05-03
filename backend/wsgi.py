"""
WSGI entrypoint for production deployments.

Railway and other WSGI hosts can point to `backend.wsgi:app`.
The module adjusts `sys.path` so the sibling `app` package can be imported
reliably regardless of the process working directory.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

app = create_app()
