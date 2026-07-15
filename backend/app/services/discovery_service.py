"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     discovery_service.py

 Description:
     Connects network discovery results with the persistent
     HomeLab Hub device inventory.

     The service creates new devices, updates existing devices
     and returns a summary of the completed synchronization.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.discovery import NetworkScanner

from .device_service import create_device
from .device_service import get_device_by_mac
from .device_service import update_device_from_discovery


@dataclass(slots=True)
class DiscoverySyncResult:
    """
    Summarize one completed discovery synchronization.

    The result can later be returned through the REST API and
    displayed after the user presses the manual Sync button.
    """

    detected: int = 0
    created: int = 0
    updated: int = 0
    skipped_without_mac: int = 0


def synchronize_discovered_devices(
    database_session: Session,
    scanner: NetworkScanner,
    network: str,
) -> DiscoverySyncResult:
    """
    Scan a network and synchronize reliable results.

    MAC addresses are currently required for persistent device
    identity. Observations without a MAC address are counted but
    not written to the database because IP addresses may change.

    Args:
        database_session:
            Active SQLAlchemy database session.

        scanner:
            Discovery implementation used to scan the network.

        network:
            Network target in CIDR notation.

    Returns:
        Summary describing how many devices were detected,
        created, updated or skipped.
    """

    discovered_devices = scanner.scan(network)

    result = DiscoverySyncResult(
        detected=len(discovered_devices),
    )

    for discovered_device in discovered_devices:
        if not discovered_device.mac_address:
            result.skipped_without_mac += 1
            continue

        normalized_mac = discovered_device.mac_address.strip().lower()

        existing_device = get_device_by_mac(
            database_session,
            normalized_mac,
        )

        if existing_device is None:
            create_device(
                database_session,
                mac_address=normalized_mac,
                hostname=discovered_device.hostname,
                current_ip=discovered_device.ip_address,
                manufacturer=discovered_device.manufacturer,
                online=True,
            )

            result.created += 1
            continue

        update_device_from_discovery(
            database_session,
            existing_device,
            hostname=discovered_device.hostname,
            current_ip=discovered_device.ip_address,
            manufacturer=discovered_device.manufacturer,
        )

        result.updated += 1

    return result
