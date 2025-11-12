"""
Vercel serverless function entry point for FastAPI application.
"""

from app.main import app

# Vercel expects a variable named 'app' or a handler function
handler = app
