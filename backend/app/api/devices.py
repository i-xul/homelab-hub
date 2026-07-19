"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     devices.py

 Description:
     Provides REST API endpoints for reading HomeLab Hub
     inventory device data.

     The API returns JSON representations that can be consumed
     by the web interface, mobile clients and optional
     integrations.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import Blueprint
from flask import jsonify

from app.database import SessionLocal
from app.models import Device
from app.services import get_inventory_devices


devices_bp = Blueprint(
    "devices",
    __name__,
)


# ---------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------


def _serialize_datetime(
    value: datetime | None,
) -> str | None:
    """
    Convert an optional datetime into an ISO 8601 string.

    Args:
        value:
            Datetime value to serialize.

    Returns:
        ISO 8601 formatted string, or None when no timestamp
        is available.
    """

    if value is None:
        return None

    return value.isoformat()


def _serialize_device(
    device: Device,
) -> dict[str, Any]:
    """
    Convert a Device database model into API-safe JSON data.

    Database models are not returned directly so that the API
    format remains independent from SQLAlchemy internals.

    Args:
        device:
            Device instance to serialize.

    Returns:
        Dictionary containing public inventory device data.
    """

    return {
        "id": device.id,
        "mac_address": device.mac_address,
        "manufacturer": device.manufacturer,
        "model": device.model,
        "device_type": device.device_type,
        "hostname": device.hostname,
        "friendly_name": device.friendly_name,
        "current_ip": device.current_ip,
        "ip_assignment": device.ip_assignment,
        "expected_ip": device.expected_ip,
        "online": device.online,
        "trusted": device.trusted,
        "pinned": device.pinned,
        "last_discovery_at": _serialize_datetime(device.last_discovery_at),
        "consecutive_missed_scans": (device.consecutive_missed_scans),
        "created_at": _serialize_datetime(device.created_at),
        "updated_at": _serialize_datetime(device.updated_at),
    }


# ---------------------------------------------------------
# Device endpoints
# ---------------------------------------------------------


@devices_bp.get("/devices")
def list_devices():
    """
    Return every device stored in the inventory.

    Devices are ordered by the service layer so that online and
    pinned devices appear first.

    Returns:
        JSON response containing the device list and summary
        counts.
    """

    with SessionLocal() as database_session:
        devices = get_inventory_devices(database_session)

        serialized_devices = [_serialize_device(device) for device in devices]

    online_count = sum(1 for device in serialized_devices if device["online"])

    unknown_count = sum(1 for device in serialized_devices if not device["trusted"])

    return jsonify(
        {
            "devices": serialized_devices,
            "summary": {
                "total": len(serialized_devices),
                "online": online_count,
                "offline": (len(serialized_devices) - online_count),
                "unknown": unknown_count,
            },
        }
    )
