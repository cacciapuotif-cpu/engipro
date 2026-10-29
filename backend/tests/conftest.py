"""
Pytest configuration — runs before any test module imports the app.
"""
import os

# Test fixtures create their own schema; use SQLite without PostgreSQL.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
