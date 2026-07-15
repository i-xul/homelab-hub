"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     models.py

 Description:
     Defines lightweight data models used during network
     discovery.

     These models represent temporary discovery results and
     are intentionally kept separate from the SQLAlchemy
     database models.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DiscoveredDevice:
    """
    Represents one device detected during a network scan.

    Instances of this class exist only in memory while a scan
    is running.

    They are later converted into persistent Device objects
    by the service layer.
    """

    ip_address: str
    mac_address: str | None = None
    hostname: str | None = None
    manufacturer: str | None = None