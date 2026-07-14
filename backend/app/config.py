"""Application configuration for HomeLab Hub."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"


class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-secret-key")
    DATABASE_PATH = INSTANCE_DIR / "homelab_hub.sqlite3"

    JSON_SORT_KEYS = False
