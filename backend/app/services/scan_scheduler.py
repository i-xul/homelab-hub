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
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from datetime import timedelta

from app.discovery import DiscoveryError
from app.settings import SCAN_INTERVAL_SECONDS

from .scan_coordinator import execute_inventory_scan
from .scan_coordinator import ScanBusyError


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Background scan scheduler
# ---------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ScanSchedulerStatus:
    """Describe the current background scan scheduler state."""

    running: bool
    interval_seconds: int
    last_scan_started_at: datetime | None
    last_scan_finished_at: datetime | None
    next_scan_at: datetime | None


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
        self._last_scan_started_at: datetime | None = None
        self._last_scan_finished_at: datetime | None = None
        self._next_scan_at: datetime | None = None

    @property
    def is_running(self) -> bool:
        """Return whether the scheduler thread is currently alive."""

        with self._state_lock:
            return self._thread is not None and self._thread.is_alive()

    @property
    def status(self) -> ScanSchedulerStatus:
        """Return a thread-safe snapshot of scheduler state."""

        with self._state_lock:
            running = self._thread is not None and self._thread.is_alive()

            return ScanSchedulerStatus(
                running=running,
                interval_seconds=self._interval_seconds,
                last_scan_started_at=self._last_scan_started_at,
                last_scan_finished_at=self._last_scan_finished_at,
                next_scan_at=self._next_scan_at,
            )

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
            self._next_scan_at = datetime.now(UTC) + timedelta(
                seconds=self._interval_seconds
            )

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
            with self._state_lock:
                self._next_scan_at = None

            self._execute_scheduled_scan()

            if self._stop_event.is_set():
                break

            with self._state_lock:
                self._next_scan_at = datetime.now(UTC) + timedelta(
                    seconds=self._interval_seconds
                )

        with self._state_lock:
            self._next_scan_at = None

    def _execute_scheduled_scan(self) -> None:
        """Attempt one automatic inventory scan."""

        scan_started_at = datetime.now(UTC)

        with self._state_lock:
            self._last_scan_started_at = scan_started_at

        try:
            execution = execute_inventory_scan(
                track_missing_devices=True,
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

        with self._state_lock:
            self._last_scan_finished_at = execution.finished_at

        logger.info(
            "Scheduled inventory scan completed: "
            "detected=%s created=%s updated=%s "
            "skipped_without_mac=%s missed=%s "
            "marked_offline=%s.",
            result.detected,
            result.created,
            result.updated,
            result.skipped_without_mac,
            result.missed,
            result.marked_offline,
        )
