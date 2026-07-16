"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     routes.py

 Description:
     Provides server-rendered web routes for the HomeLab Hub
     browser interface.

     The initial dashboard displays inventory summary data,
     active devices, pinned offline devices and other offline
     devices.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from flask import Blueprint
from flask import render_template

from app.database import SessionLocal
from app.models import Device
from app.services import get_inventory_devices


web_bp = Blueprint(
    "web",
    __name__,
)


# ---------------------------------------------------------
# Dashboard helpers
# ---------------------------------------------------------


def _get_display_name(device: Device) -> str:
    """
    Return the most useful display name available for a device.

    User-defined friendly names have priority over automatically
    discovered hostnames. The MAC address is used as a final
    fallback when neither name is available.

    Args:
        device:
            Inventory device whose display name is required.

    Returns:
        Human-readable name for the browser interface.
    """

    return device.friendly_name or device.hostname or device.mac_address


# ---------------------------------------------------------
# Dashboard routes
# ---------------------------------------------------------


@web_bp.get("/")
def dashboard():
    """
    Render the main HomeLab Hub inventory dashboard.

    Online devices and all pinned devices are displayed in the
    primary Devices section. Non-pinned offline devices appear
    in the separate Offline section.

    Returns:
        Rendered dashboard HTML response.
    """

    with SessionLocal() as database_session:
        inventory_devices = get_inventory_devices(database_session)

        # Copy the required model data before the database
        # session closes. The template receives plain
        # dictionaries rather than attached SQLAlchemy models.
        devices = [
            {
                "id": device.id,
                "display_name": _get_display_name(device),
                "hostname": device.hostname,
                "friendly_name": device.friendly_name,
                "current_ip": device.current_ip,
                "mac_address": device.mac_address,
                "manufacturer": device.manufacturer,
                "online": device.online,
                "trusted": device.trusted,
                "pinned": device.pinned,
                "last_discovery_at": device.last_discovery_at,
                "consecutive_missed_scans": (device.consecutive_missed_scans),
            }
            for device in inventory_devices
        ]

    primary_devices = [
        device for device in devices if device["online"] or device["pinned"]
    ]

    offline_devices = [
        device for device in devices if not device["online"] and not device["pinned"]
    ]

    online_count = sum(1 for device in devices if device["online"])

    unknown_count = sum(1 for device in devices if not device["trusted"])

    summary = {
        "total": len(devices),
        "online": online_count,
        "offline": len(devices) - online_count,
        "unknown": unknown_count,
    }

    return render_template(
        "dashboard.html",
        primary_devices=primary_devices,
        offline_devices=offline_devices,
        summary=summary,
    )
