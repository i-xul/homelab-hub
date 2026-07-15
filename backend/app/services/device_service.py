"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     device_service.py

 Description:
     Provides database operations for creating, retrieving and
     updating devices managed by HomeLab Hub.

     This service layer keeps database logic separate from API
     endpoints, network discovery and user-interface code.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Device


# ---------------------------------------------------------
# Device lookup
# ---------------------------------------------------------


def get_device_by_mac(
    database_session: Session,
    mac_address: str,
) -> Device | None:
    """
    Return a device matching the supplied MAC address.

    MAC addresses are normalized before the database query so
    that differences in letter case do not create duplicates.

    Args:
        database_session:
            Active SQLAlchemy database session.

        mac_address:
            Device MAC address to search for.

    Returns:
        Matching Device instance, or None when no device exists.
    """

    normalized_mac = mac_address.strip().lower()

    statement = select(Device).where(Device.mac_address == normalized_mac)

    return database_session.scalar(statement)


# ---------------------------------------------------------
# Device creation
# ---------------------------------------------------------


def create_device(
    database_session: Session,
    *,
    mac_address: str,
    hostname: str | None = None,
    current_ip: str | None = None,
    manufacturer: str | None = None,
    online: bool = False,
) -> Device:
    """
    Create and persist a new device.

    The MAC address is normalized before storage. This function
    raises ValueError if a device with the same MAC address is
    already present in the inventory.

    Args:
        database_session:
            Active SQLAlchemy database session.

        mac_address:
            Unique MAC address identifying the device.

        hostname:
            Hostname reported by network discovery, if available.

        current_ip:
            Current IPv4 or IPv6 address, if available.

        manufacturer:
            Hardware manufacturer, if available.

        online:
            Whether the device was online when it was created.

    Returns:
        Newly created and persisted Device instance.

    Raises:
        ValueError:
            If the supplied MAC address is empty or already
            belongs to an existing device.
    """

    normalized_mac = mac_address.strip().lower()

    if not normalized_mac:
        raise ValueError("MAC address must not be empty.")

    existing_device = get_device_by_mac(
        database_session,
        normalized_mac,
    )

    if existing_device is not None:
        raise ValueError(f"Device already exists for MAC address {normalized_mac}.")

    device = Device(
        mac_address=normalized_mac,
        hostname=hostname,
        current_ip=current_ip,
        manufacturer=manufacturer,
        online=online,
        trusted=False,
        pinned=False,
    )

    database_session.add(device)
    database_session.commit()
    database_session.refresh(device)

    return device


# ---------------------------------------------------------
# Device discovery updates
# ---------------------------------------------------------


def update_device_from_discovery(
    database_session: Session,
    device: Device,
    *,
    hostname: str | None,
    current_ip: str,
    manufacturer: str | None,
) -> Device:
    """
    Update automatically collected information for a device.

    Only discovery-managed fields are modified. Friendly names,
    tags, trust status and other user-managed information remain
    unchanged.

    Args:
        database_session:
            Active SQLAlchemy database session.

        device:
            Existing Device instance to update.

        hostname:
            Hostname reported by the latest discovery scan.

        current_ip:
            Current network address reported by discovery.

        manufacturer:
            Manufacturer reported by Nmap, if available.

    Returns:
        Updated and persisted Device instance.
    """

    device.current_ip = current_ip
    device.online = True

    # Do not erase previously discovered information merely
    # because a later scan could not resolve the same value.
    if hostname:
        device.hostname = hostname

    if manufacturer:
        device.manufacturer = manufacturer

    database_session.commit()
    database_session.refresh(device)

    return device


def mark_device_offline(
    database_session: Session,
    device: Device,
) -> Device:
    """
    Mark a device as offline without removing it.

    Devices remain permanently in the inventory until the user
    explicitly removes them.

    Args:
        database_session:
            Active SQLAlchemy database session.

        device:
            Device that was not present in the completed scan.

    Returns:
        Updated and persisted Device instance.
    """

    device.online = False

    database_session.commit()
    database_session.refresh(device)

    return device
