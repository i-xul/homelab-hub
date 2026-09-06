"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     service.py

 Description:
     Production service entry point for HomeLab Hub.

     Creates the Flask application and starts the background
     inventory scan scheduler without relying on Flask's
     development reloader.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

import atexit

from app import create_app
from app.services import InventoryScanScheduler


app = create_app()

scheduler = InventoryScanScheduler()
app.extensions["inventory_scan_scheduler"] = scheduler

scheduler.start()
atexit.register(scheduler.stop)
