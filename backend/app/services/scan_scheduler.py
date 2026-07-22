"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     scan_scheduler.py

 Description:
     Provides the background scheduler used to run automatic
     HomeLab Hub inventory scans at a configurable interval.

     Scheduled scans use the shared scan coordinator so that
     automatic and manually requested scans cannot overlap.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

import logging
from threading import current_thread
from threading import Event
from threading import Lock
from threading import Thread

from app.discovery import DiscoveryError
from app.settings import SCAN_INTERVAL_SECONDS

from .scan_coordinator import execute_inventory_scan
from .scan_coordinator import ScanBusyError


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Background scan scheduler
# ---------------------------------------------------------


class InventoryScanScheduler:
    """
    Run inventory scans periodically in a background thread.

    The scheduler waits for one complete interval before the
    first automatic scan. This avoids starting network discovery
    immediately while the application itself is still starting.

    Only one scheduler thread may be started per scheduler
    instance.
    """

    def __init__(
        self,
        *,
        interval_seconds: int = SCAN_INTERVAL_SECONDS,
    ) -> None:
        """
        Initialize the background scan scheduler.

        Args:
            interval_seconds:
                Number of seconds between automatic scan
                attempts.

        Raises:
            ValueError:
                If interval_seconds is less than one.
        """

        if interval_seconds < 1:
            raise ValueError("Scan interval must be at least one second.")

        self._interval_seconds = interval_seconds
        self._stop_event = Event()
        self._state_lock = Lock()
        self._thread: Thread | None = None

    @property
    def is_running(self) -> bool:
        """Return whether the scheduler thread is currently alive."""

        with self._state_lock:
            return self._thread is not None and self._thread.is_alive()

    def start(self) -> bool:
        """
        Start the background scheduler.

        Returns:
            True when a new scheduler thread was started.
            False when the scheduler was already running.
        """

        with self._state_lock:
            if self._thread is not None and self._thread.is_alive():
                return False

            self._stop_event.clear()

            self._thread = Thread(
                target=self._run,
                name="homelab-hub-scan-scheduler",
                daemon=True,
            )

            self._thread.start()

        logger.info(
            "Inventory scan scheduler started with %s second interval.",
            self._interval_seconds,
        )

        return True

    def stop(self) -> None:
        """Request the background scheduler to stop.

        If a scheduled inventory scan is currently running, wait
        for it to finish before returning.
        """

        self._stop_event.set()

        with self._state_lock:
            thread = self._thread

        if thread is not None and thread.is_alive() and thread is not current_thread():
            thread.join()

    def _run(self) -> None:
        """Wait for scan intervals and execute scheduled scans."""

        while not self._stop_event.wait(self._interval_seconds):
            self._execute_scheduled_scan()

    @staticmethod
    def _execute_scheduled_scan() -> None:
        """Attempt one automatic inventory scan."""

        try:
            execution = execute_inventory_scan(
                track_missing_devices=False,
            )
        except ScanBusyError:
            logger.info(
                "Scheduled inventory scan skipped because "
                "another scan is already running."
            )
            return
        except DiscoveryError as error:
            logger.error(
                "Scheduled inventory scan failed: %s",
                error,
            )
            return
        except Exception:
            logger.exception("Unexpected error during scheduled inventory scan.")
            return

        result = execution.result

        logger.info(
            "Scheduled inventory scan completed: "
            "detected=%s created=%s updated=%s "
            "skipped_without_mac=%s.",
            result.detected,
            result.created,
            result.updated,
            result.skipped_without_mac,
        )
