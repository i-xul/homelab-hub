"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     scan.py

 Description:
     Provides the REST API endpoint used to start a manual
     HomeLab Hub inventory scan.

     A process-level lock prevents multiple scans from running
     simultaneously inside the same backend process.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from datetime import UTC, datetime
from threading import Lock

from flask import Blueprint
from flask import jsonify

from app.database import SessionLocal
from app.discovery import DiscoveryError
from app.services import run_inventory_scan


scan_bp = Blueprint(
    "scan",
    __name__,
)


# ---------------------------------------------------------
# Scan state
# ---------------------------------------------------------

# Nmap scans must not overlap. A later background scheduler and
# the manual API endpoint will both use the same locking rule.
_scan_lock = Lock()


# ---------------------------------------------------------
# Manual scan endpoint
# ---------------------------------------------------------


@scan_bp.post("/scan")
def start_manual_scan():
    """
    Run one manual inventory scan.

    Missing-device tracking is deliberately disabled until the
    configured scanner provides reliable MAC-address coverage.
    This prevents incomplete scans from incorrectly marking the
    complete inventory offline.

    Returns:
        JSON response containing scan statistics.

        HTTP 200:
            Scan completed successfully.

        HTTP 409:
            Another scan is already running.

        HTTP 500:
            Discovery failed before completing.
    """

    scan_started_at = datetime.now(UTC)

    # Acquire without waiting so the browser receives an
    # immediate response when another scan is already active.
    if not _scan_lock.acquire(blocking=False):
        return (
            jsonify(
                {
                    "status": "busy",
                    "message": ("Another inventory scan is already running."),
                }
            ),
            409,
        )

    try:
        with SessionLocal() as database_session:
            result = run_inventory_scan(
                database_session,
                track_missing_devices=False,
            )
    except DiscoveryError as error:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": str(error),
                    "started_at": scan_started_at.isoformat(),
                    "finished_at": datetime.now(UTC).isoformat(),
                }
            ),
            500,
        )
    finally:
        _scan_lock.release()

    scan_finished_at = datetime.now(UTC)

    return jsonify(
        {
            "status": "completed",
            "started_at": scan_started_at.isoformat(),
            "finished_at": scan_finished_at.isoformat(),
            "result": {
                "detected": result.detected,
                "created": result.created,
                "updated": result.updated,
                "skipped_without_mac": (result.skipped_without_mac),
                "missed": result.missed,
                "marked_offline": result.marked_offline,
            },
        }
    )
