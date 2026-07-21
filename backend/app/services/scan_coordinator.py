"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     scan_coordinator.py

 Description:
     Coordinates inventory scan execution across manual API
     requests and background scheduling.

     A shared process-level lock prevents overlapping Nmap
     scans inside the same HomeLab Hub backend process.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock

from app.database import SessionLocal

from .discovery_service import DiscoverySyncResult
from .inventory_service import run_inventory_scan


# ---------------------------------------------------------
# Scan execution result
# ---------------------------------------------------------


@dataclass(frozen=True, slots=True)
class InventoryScanExecution:
    """Describe one successfully completed inventory scan."""

    started_at: datetime
    finished_at: datetime
    result: DiscoverySyncResult


# ---------------------------------------------------------
# Scan coordination errors
# ---------------------------------------------------------


class ScanBusyError(RuntimeError):
    """Raised when another inventory scan is already running."""


# ---------------------------------------------------------
# Shared process-level scan state
# ---------------------------------------------------------

# Manual and scheduled scans must use this same lock. Acquiring
# it without waiting allows callers to react immediately when
# another scan is already in progress.
_scan_lock = Lock()


# ---------------------------------------------------------
# Coordinated inventory scan
# ---------------------------------------------------------


def execute_inventory_scan(
    *,
    track_missing_devices: bool = False,
) -> InventoryScanExecution:
    """
    Run one inventory scan while preventing overlapping scans.

    A new SQLAlchemy session is created for every scan so that
    manual requests and background jobs do not share database
    session state.

    Args:
        track_missing_devices:
            Whether online devices absent from the completed
            scan should receive a missed-scan count.

    Returns:
        InventoryScanExecution containing timestamps and scan
        statistics.

    Raises:
        ScanBusyError:
            If another inventory scan is already running.

        DiscoveryError:
            If network discovery cannot complete successfully.
    """

    if not _scan_lock.acquire(blocking=False):
        raise ScanBusyError("Another inventory scan is already running.")

    started_at = datetime.now(UTC)

    try:
        with SessionLocal() as database_session:
            result = run_inventory_scan(
                database_session,
                track_missing_devices=track_missing_devices,
            )

        finished_at = datetime.now(UTC)

        return InventoryScanExecution(
            started_at=started_at,
            finished_at=finished_at,
            result=result,
        )
    finally:
        _scan_lock.release()
