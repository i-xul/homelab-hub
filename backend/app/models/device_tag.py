"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     device_tag.py

 Description:
     Defines the many-to-many association table connecting
     inventory devices with user-managed tags.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Table

from .base import Base


device_tags = Table(
    "device_tags",
    Base.metadata,
    Column(
        "device_id",
        Integer,
        ForeignKey(
            "devices.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey(
            "tags.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)
