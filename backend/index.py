"""
Vercel serverless function entry point for FastAPI application.
"""

import sys
import traceback

try:
    from app.main import app as fastapi_app
    # Vercel expects a variable named 'app'
    app = fastapi_app
except Exception as e:
    # Print detailed error for debugging
    print(f"ERROR loading app: {e}", file=sys.stderr)
    print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
    raise
