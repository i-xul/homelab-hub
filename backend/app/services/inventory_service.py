"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     inventory_service.py

 Description:
     Provides the high-level inventory scan cycle used by
     scheduled scans, manual synchronization and future API
     clients.

     The service combines network discovery with persistent
     inventory synchronization while keeping scanner-specific
     logic outside the caller.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.discovery import NetworkScanner
from app.discovery import NmapScanner
from app.settings import DEFAULT_NETWORK
from app.settings import NMAP_TIMEOUT_SECONDS

from .discovery_service import DiscoverySyncResult
from .discovery_service import synchronize_discovered_devices


# ---------------------------------------------------------
# Inventory scan cycle
# ---------------------------------------------------------


def run_inventory_scan(
    database_session: Session,
    *,
    scanner: NetworkScanner | None = None,
    network: str = DEFAULT_NETWORK,
    track_missing_devices: bool = False,
) -> DiscoverySyncResult:
    """
    Run one complete inventory discovery cycle.

    The default implementation uses Nmap and the configured
    network target. A custom scanner may be supplied by tests,
    optional modules or future discovery implementations.

    Missing-device tracking remains disabled by default because
    it must only be enabled when the scanner provides reliable
    MAC-address coverage for the complete target network.

    Args:
        database_session:
            Active SQLAlchemy database session.

        scanner:
            Optional discovery implementation. When omitted,
            the default Nmap scanner is created automatically.

        network:
            Network target in CIDR notation.

        track_missing_devices:
            Whether online devices absent from the completed
            scan should receive a missed-scan count.

    Returns:
        DiscoverySyncResult containing the completed scan
        statistics.

    Raises:
        DiscoveryError:
            If the selected scanner cannot complete the scan.
    """

    active_scanner = scanner or NmapScanner(
        timeout_seconds=NMAP_TIMEOUT_SECONDS,
    )

    return synchronize_discovered_devices(
        database_session,
        active_scanner,
        network,
        track_missing_devices=track_missing_devices,
    )
