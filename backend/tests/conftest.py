"""
Pytest configuration — runs before any test module imports the app.
"""
import os

# Point application configuration at SQLite; fixtures create their own schema.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
