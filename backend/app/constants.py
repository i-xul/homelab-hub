"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     constants.py

 Description:
     Stores application-wide constants used throughout
     the HomeLab Hub project.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

# ---------------------------------------------------------
# Network discovery
# ---------------------------------------------------------

DEFAULT_SCAN_INTERVAL = 300  # seconds

# ---------------------------------------------------------
# Backend
# ---------------------------------------------------------

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000

# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

DATABASE_FILENAME = "homelab_hub.sqlite3"