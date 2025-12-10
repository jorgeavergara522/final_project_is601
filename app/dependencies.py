# app/dependencies.py
# This file exists ONLY so tests importing app.dependencies do not fail.

from app.database import get_db

__all__ = ["get_db"]
