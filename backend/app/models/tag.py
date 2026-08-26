"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     tag.py

 Description:
     Defines user-managed tags used to classify and group
     HomeLab Hub inventory devices.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base
from .device_tag import device_tags
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .device import Device


class Tag(Base, TimestampMixin):
    """
    Represents one reusable inventory tag.

    Tags are user-managed labels that may be assigned to any
    number of devices. One device may also have multiple tags.
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    color: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    devices: Mapped[list["Device"]] = relationship(
        secondary=device_tags,
        back_populates="tags",
    )
