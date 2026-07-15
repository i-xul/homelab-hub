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


__all__ = [
    "create_device",
    "get_device_by_mac",
]