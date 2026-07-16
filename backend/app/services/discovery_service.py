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
     and records continuous online sessions for successfully
     detected devices.

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
from .device_session_service import record_device_seen
from .device_service import get_all_devices
from .device_session_service import record_device_missed


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
    missed: int = 0
    marked_offline: int = 0


def synchronize_discovered_devices(
    database_session: Session,
    scanner: NetworkScanner,
    network: str,
    *,
    track_missing_devices: bool = False,
) -> DiscoverySyncResult:
    """
    Scan a network and synchronize reliable discovery results.

    MAC addresses are currently required for persistent device
    identity. Observations without a MAC address are counted but
    not written to the database because IP addresses may change.

    Every successfully synchronized device also receives an
    open online session. Later observations update the same
    session instead of creating duplicate sessions.

    Args:
        database_session:
            Active SQLAlchemy database session.

        scanner:
            Discovery implementation used to scan the network.

        network:
            Network target in CIDR notation.

        track_missing_devices:
            Whether devices absent from this scan should receive
            a missed-scan count. This must only be enabled when
            the scan returns reliable MAC-address coverage.

    Returns:
        Summary describing how many devices were detected,
        created, updated or skipped.
    """

    discovered_devices = scanner.scan(network)

    result = DiscoverySyncResult(
        detected=len(discovered_devices),
    )

    observed_mac_addresses: set[str] = set()
    for discovered_device in discovered_devices:
        if not discovered_device.mac_address:
            result.skipped_without_mac += 1
            continue

        normalized_mac = discovered_device.mac_address.strip().lower()

        existing_device = get_device_by_mac(
            database_session,
            normalized_mac,
        )

        observed_mac_addresses.add(normalized_mac)

        if existing_device is None:
            device = create_device(
                database_session,
                mac_address=normalized_mac,
                hostname=discovered_device.hostname,
                current_ip=discovered_device.ip_address,
                manufacturer=discovered_device.manufacturer,
                online=True,
            )

            # Open the device's first online session.
            record_device_seen(
                database_session,
                device,
            )

            result.created += 1
            continue

        device = update_device_from_discovery(
            database_session,
            existing_device,
            hostname=discovered_device.hostname,
            current_ip=discovered_device.ip_address,
            manufacturer=discovered_device.manufacturer,
        )

        # Refresh the existing online session without creating
        # another session for the same continuous online period.
        record_device_seen(
            database_session,
            device,
        )

        result.updated += 1

    # Missing-device processing is intentionally optional.
    # A scan without reliable MAC-address coverage must never
    # mark the complete inventory offline.
    if track_missing_devices:
        for stored_device in get_all_devices(database_session):
            if stored_device.mac_address in observed_mac_addresses:
                continue

            if not stored_device.online:
                continue

            result.missed += 1

            changed_to_offline = record_device_missed(
                database_session,
                stored_device,
            )

            if changed_to_offline:
                result.marked_offline += 1

    return result
