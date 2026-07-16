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


__all__ = [
    "close_device_session",
    "create_device",
    "DiscoverySyncResult",
    "get_all_devices",
    "get_device_by_mac",
    "get_open_device_session",
    "mark_device_offline",
    "record_device_missed",
    "record_device_seen",
    "synchronize_discovered_devices",
    "update_device_from_discovery",
]
