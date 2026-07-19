"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     device.py

 Description:
     Defines the primary Device model used by HomeLab Hub.

     Every discovered or manually created device is represented
     by exactly one Device instance.

     Devices are never removed automatically.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .mixins import TimestampMixin

from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .device_session import DeviceSession


class Device(Base, TimestampMixin):
    """
    Represents one device managed by HomeLab Hub.

    Devices may originate from automatic discovery or be
    created manually by the user.

    User supplied information always has priority over
    automatically discovered values.
    """

    __tablename__ = "devices"

    # ---------------------------------------------------------
    # Primary identifier
    # ---------------------------------------------------------

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # ---------------------------------------------------------
    # Device identity
    # ---------------------------------------------------------

    mac_address: Mapped[str] = mapped_column(
        String(17),
        unique=True,
        nullable=False,
        index=True,
    )

    manufacturer: Mapped[str | None] = mapped_column(
        String(100),
    )

    model: Mapped[str | None] = mapped_column(
        String(100),
    )

    device_type: Mapped[str | None] = mapped_column(
        String(50),
    )

    # ---------------------------------------------------------
    # Current network state
    # ---------------------------------------------------------

    hostname: Mapped[str | None] = mapped_column(
        String(255),
    )

    current_ip: Mapped[str | None] = mapped_column(
        String(45),
    )

    online: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Discovery state
    # ---------------------------------------------------------

    last_discovery_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    consecutive_missed_scans: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ---------------------------------------------------------
    # User-managed information
    # ---------------------------------------------------------

    friendly_name: Mapped[str | None] = mapped_column(
        String(255),
    )

    # ---------------------------------------------------------
    # User-managed network configuration
    # ---------------------------------------------------------

    ip_assignment: Mapped[str] = mapped_column(
        String(20),
        default="unknown",
        nullable=False,
    )

    expected_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    trusted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    sessions: Mapped[list["DeviceSession"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        order_by="DeviceSession.session_start",
    )
