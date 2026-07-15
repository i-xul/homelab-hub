"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     device_session.py

 Description:
     Defines the DeviceSession model used to track continuous
     periods during which a device is visible on the network.

     A new session begins when an offline device is detected.
     The session remains open while the device continues to
     appear in network scans and ends when the configured
     offline threshold is reached.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base
from .mixins import TimestampMixin


if TYPE_CHECKING:
    from .device import Device


class DeviceSession(Base, TimestampMixin):
    """
    Represents one continuous online period for a device.

    The session starts when a device is first detected after
    being offline. The last_seen value is refreshed after each
    successful scan. The session is closed only after the
    device has missed the configured number of scans.

    Session duration is calculated from stored timestamps
    instead of being stored as duplicate database data.
    """

    __tablename__ = "device_sessions"

    # ---------------------------------------------------------
    # Primary identifier
    # ---------------------------------------------------------

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # ---------------------------------------------------------
    # Device relationship
    # ---------------------------------------------------------

    device_id: Mapped[int] = mapped_column(
        ForeignKey(
            "devices.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------------------
    # Session timestamps
    # ---------------------------------------------------------

    session_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    session_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    device: Mapped["Device"] = relationship(
        back_populates="sessions",
    )

    # ---------------------------------------------------------
    # Calculated properties
    # ---------------------------------------------------------

    @property
    def duration_seconds(self) -> int:
        """
        Return the session duration in whole seconds.

        A closed session uses session_end as its endpoint.
        An open session uses the latest successful discovery
        timestamp stored in last_seen.
        """

        endpoint = self.session_end or self.last_seen
        duration = endpoint - self.session_start

        return max(0, int(duration.total_seconds()))