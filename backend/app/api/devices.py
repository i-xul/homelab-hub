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

import ipaddress

from flask import request

from app.services import get_device_by_id
from app.services import update_device_metadata


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
# Validation helpers
# ---------------------------------------------------------

ALLOWED_IP_ASSIGNMENTS = {
    "unknown",
    "dhcp",
    "reserved",
    "static",
}


def _validate_expected_ip(
    value: str | None,
) -> str | None:
    """
    Validate an optional IPv4 or IPv6 address.

    Empty strings are normalized to None.

    Args:
        value:
            User-supplied IP address.

    Returns:
        Normalized IP address string or None.

    Raises:
        ValueError:
            If the value is not a valid IP address.
    """

    if value is None:
        return None

    normalized_value = value.strip()

    if not normalized_value:
        return None

    try:
        return str(ipaddress.ip_address(normalized_value))
    except ValueError as error:
        raise ValueError("Expected IP address is not valid.") from error


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


@devices_bp.patch("/devices/<int:device_id>")
def update_device(device_id: int):
    """
    Update user-managed metadata for one inventory device.

    Supported fields:

    - friendly_name
    - trusted
    - pinned
    - ip_assignment
    - expected_ip

    Returns:
        HTTP 200 with the updated device on success.

        HTTP 400 when request data is invalid.

        HTTP 404 when the requested device does not exist.
    """

    payload = request.get_json(
        silent=True,
    )

    if not isinstance(payload, dict):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": ("Request body must contain a JSON object."),
                }
            ),
            400,
        )

    allowed_fields = {
        "friendly_name",
        "trusted",
        "pinned",
        "ip_assignment",
        "expected_ip",
    }

    unexpected_fields = set(payload) - allowed_fields

    if unexpected_fields:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": (
                        "Unsupported fields: " + ", ".join(sorted(unexpected_fields))
                    ),
                }
            ),
            400,
        )

    if "trusted" in payload and not isinstance(
        payload["trusted"],
        bool,
    ):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": ("trusted must be a boolean."),
                }
            ),
            400,
        )

    if "pinned" in payload and not isinstance(
        payload["pinned"],
        bool,
    ):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": ("pinned must be a boolean."),
                }
            ),
            400,
        )

    ip_assignment = payload.get("ip_assignment")

    if ip_assignment is not None and ip_assignment not in ALLOWED_IP_ASSIGNMENTS:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": (
                        "ip_assignment must be one of: unknown, dhcp, reserved, static."
                    ),
                }
            ),
            400,
        )

    try:
        expected_ip = (
            _validate_expected_ip(payload.get("expected_ip"))
            if "expected_ip" in payload
            else None
        )
    except ValueError as error:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": str(error),
                }
            ),
            400,
        )

    with SessionLocal() as database_session:
        device = get_device_by_id(
            database_session,
            device_id,
        )

        if device is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Device not found.",
                    }
                ),
                404,
            )

        updated_device = update_device_metadata(
            database_session,
            device,
            friendly_name=payload.get("friendly_name")
            if "friendly_name" in payload
            else None,
            trusted=payload.get("trusted") if "trusted" in payload else None,
            pinned=payload.get("pinned") if "pinned" in payload else None,
            ip_assignment=ip_assignment,
            expected_ip=expected_ip if "expected_ip" in payload else None,
        )

        response_data = _serialize_device(updated_device)

    return jsonify(
        {
            "status": "updated",
            "device": response_data,
        }
    )
