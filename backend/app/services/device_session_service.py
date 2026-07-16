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
from app.settings import OFFLINE_SCAN_THRESHOLD


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

    # A successful observation resets the device presence state.
    device.online = True
    device.last_discovery_at = observation_time
    device.consecutive_missed_scans = 0

    database_session.commit()
    database_session.refresh(open_session)

    return open_session


# ---------------------------------------------------------
# Missing-device handling
# ---------------------------------------------------------


def close_device_session(
    database_session: Session,
    device: Device,
) -> DeviceSession | None:
    """
    Close the currently open online session for a device.

    The session is closed at its latest successful last_seen
    timestamp rather than at the later time when the offline
    threshold is finally reached.

    Args:
        database_session:
            Active SQLAlchemy database session.

        device:
            Device whose open session should be closed.

    Returns:
        Closed DeviceSession instance, or None when the device
        did not have an open session.
    """

    open_session = get_open_device_session(
        database_session,
        device.id,
    )

    if open_session is None:
        return None

    open_session.session_end = open_session.last_seen

    database_session.commit()
    database_session.refresh(open_session)

    return open_session


def record_device_missed(
    database_session: Session,
    device: Device,
    *,
    offline_threshold: int = OFFLINE_SCAN_THRESHOLD,
) -> bool:
    """
    Record one completed scan in which a device was not found.

    An online device remains online until the configured number
    of consecutive missed scans has been reached. When the
    threshold is reached, the device is marked offline and its
    open session is closed.

    Already offline devices are left unchanged.

    Args:
        database_session:
            Active SQLAlchemy database session.

        device:
            Device missing from the completed discovery scan.

        offline_threshold:
            Number of consecutive misses required before the
            device is marked offline.

    Returns:
        True when this call changed the device from online to
        offline. Otherwise False.

    Raises:
        ValueError:
            If offline_threshold is less than one.
    """

    if offline_threshold < 1:
        raise ValueError("Offline threshold must be at least one.")

    if not device.online:
        return False

    device.consecutive_missed_scans += 1

    if device.consecutive_missed_scans < offline_threshold:
        database_session.commit()
        database_session.refresh(device)

        return False

    device.online = False

    open_session = get_open_device_session(
        database_session,
        device.id,
    )

    if open_session is not None:
        # End the session at the last confirmed observation,
        # not at the later threshold-processing timestamp.
        open_session.session_end = open_session.last_seen

    database_session.commit()
    database_session.refresh(device)

    if open_session is not None:
        database_session.refresh(open_session)

    return True
