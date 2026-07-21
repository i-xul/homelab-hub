"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     scan.py

 Description:
     Provides the REST API endpoint used to start a manual
     HomeLab Hub inventory scan.

     Manual and scheduled scans use the shared scan coordinator
     so that multiple Nmap scans cannot run simultaneously.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint
from flask import jsonify

from app.discovery import DiscoveryError
from app.services import execute_inventory_scan
from app.services import ScanBusyError


scan_bp = Blueprint(
    "scan",
    __name__,
)


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

    request_started_at = datetime.now(UTC)

    try:
        execution = execute_inventory_scan(
            track_missing_devices=False,
        )
    except ScanBusyError as error:
        return (
            jsonify(
                {
                    "status": "busy",
                    "message": str(error),
                }
            ),
            409,
        )
    except DiscoveryError as error:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": str(error),
                    "started_at": request_started_at.isoformat(),
                    "finished_at": datetime.now(UTC).isoformat(),
                }
            ),
            500,
        )

    result = execution.result

    return jsonify(
        {
            "status": "completed",
            "started_at": execution.started_at.isoformat(),
            "finished_at": execution.finished_at.isoformat(),
            "result": {
                "detected": result.detected,
                "created": result.created,
                "updated": result.updated,
                "skipped_without_mac": result.skipped_without_mac,
                "missed": result.missed,
                "marked_offline": result.marked_offline,
            },
        }
    )
