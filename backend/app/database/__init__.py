"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     __init__.py

 Description:
     Exposes the database engine, session factory and database
     initialization function used by the HomeLab Hub backend.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from .database import SessionLocal
from .database import engine
from .database import initialize_database


__all__ = [
    "engine",
    "SessionLocal",
    "initialize_database",
]