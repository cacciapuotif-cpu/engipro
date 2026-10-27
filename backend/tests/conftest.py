"""
Pytest configuration — runs before any test module imports the app.
"""
import os

# app.main creates tables at import time; point it at a local SQLite file
# so the suite runs without a PostgreSQL server.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
