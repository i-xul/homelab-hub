"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     database.py

 Description:
     Creates the SQLAlchemy engine and database session
     factory used by the HomeLab Hub backend.

     The SQLite database is stored in the backend instance
     directory so that runtime data remains separate from
     the application source code.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.constants import DATABASE_FILENAME


# ---------------------------------------------------------
# Database paths
# ---------------------------------------------------------

# Resolve the backend directory independently of the current
# working directory. This ensures that Flask, systemd and test
# commands all use the same SQLite database location.
BACKEND_DIR = Path(__file__).resolve().parents[2]
INSTANCE_DIR = BACKEND_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / DATABASE_FILENAME

# Create the runtime directory automatically if it does not
# already exist. The directory contents are excluded from Git.
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# ---------------------------------------------------------
# SQLAlchemy engine
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False,
)


# ---------------------------------------------------------
# Database session factory
# ---------------------------------------------------------

# SessionLocal creates independent database sessions for future
# requests, services and background jobs.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)