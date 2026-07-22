"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     __init__.py

 Description:
     Exposes application service functions used by the
     HomeLab Hub backend.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from .device_service import create_device
from .device_service import get_device_by_mac

from .device_service import mark_device_offline
from .device_service import update_device_from_discovery
from .discovery_service import DiscoverySyncResult
from .discovery_service import synchronize_discovered_devices
from .device_session_service import get_open_device_session
from .device_session_service import record_device_seen
from .device_service import get_all_devices
from .device_session_service import close_device_session
from .device_session_service import record_device_missed
from .inventory_service import run_inventory_scan
from .device_service import get_inventory_devices
from .device_service import get_device_by_id
from .device_service import update_device_metadata
from .device_session_service import get_device_sessions
from .scan_coordinator import execute_inventory_scan
from .scan_coordinator import InventoryScanExecution
from .scan_coordinator import ScanBusyError
from .scan_scheduler import InventoryScanScheduler


__all__ = [
    "close_device_session",
    "create_device",
    "DiscoverySyncResult",
    "execute_inventory_scan",
    "get_all_devices",
    "get_device_by_id",
    "get_device_by_mac",
    "get_device_sessions",
    "get_inventory_devices",
    "get_open_device_session",
    "InventoryScanScheduler",
    "InventoryScanExecution",
    "mark_device_offline",
    "record_device_missed",
    "record_device_seen",
    "run_inventory_scan",
    "ScanBusyError",
    "synchronize_discovered_devices",
    "update_device_from_discovery",
    "update_device_metadata",
]
