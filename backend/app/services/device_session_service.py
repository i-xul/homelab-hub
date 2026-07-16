"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     device_session_service.py

 Description:
     Provides database operations for tracking continuous
     periods during which devices are visible on the network.

     The service opens a new session when an offline device is
     detected and updates the existing open session during
     subsequent successful scans.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Device
from app.models import DeviceSession


# ---------------------------------------------------------
# Session lookup
# ---------------------------------------------------------


def get_open_device_session(
    database_session: Session,
    device_id: int,
) -> DeviceSession | None:
    """
    Return the currently open session for a device.

    An open session has no session_end timestamp. A device
    should never have more than one open session at a time.

    Args:
        database_session:
            Active SQLAlchemy database session.

        device_id:
            Database identifier of the device.

    Returns:
        Open DeviceSession instance, or None if the device
        does not currently have an open session.
    """

    statement = (
        select(DeviceSession)
        .where(
            DeviceSession.device_id == device_id,
            DeviceSession.session_end.is_(None),
        )
        .order_by(DeviceSession.session_start.desc())
    )

    return database_session.scalar(statement)


# ---------------------------------------------------------
# Successful discovery handling
# ---------------------------------------------------------


def record_device_seen(
    database_session: Session,
    device: Device,
    *,
    seen_at: datetime | None = None,
) -> DeviceSession:
    """
    Record a successful network observation for a device.

    If the device already has an open session, its last_seen
    timestamp is updated. Otherwise, a new session is opened.

    The device is also marked online.

    Args:
        database_session:
            Active SQLAlchemy database session.

        device:
            Device detected during the latest network scan.

        seen_at:
            Optional observation timestamp. Current UTC time is
            used when no explicit value is supplied.

    Returns:
        Newly created or updated DeviceSession instance.
    """

    observation_time = seen_at or datetime.now(UTC)

    open_session = get_open_device_session(
        database_session,
        device.id,
    )

    if open_session is None:
        open_session = DeviceSession(
            device_id=device.id,
            session_start=observation_time,
            last_seen=observation_time,
        )

        database_session.add(open_session)
    else:
        open_session.last_seen = observation_time

    device.online = True

    database_session.commit()
    database_session.refresh(open_session)

    return open_session
