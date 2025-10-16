"""Vercel serverless function entry point for FastAPI backend."""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Set environment for serverless
os.environ.setdefault('ENVIRONMENT', 'production')

# Import the FastAPI app
from app.main import app

# Vercel requires this exact export
app = app
