"""Vercel serverless function entry point for FastAPI backend."""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app

# Export for Vercel
handler = app
