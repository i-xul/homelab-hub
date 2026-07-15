"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     mixins.py

 Description:
     Provides reusable SQLAlchemy mixin classes shared by
     multiple database models.

     Mixins reduce duplicated code by supplying commonly
     used columns and functionality.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class TimestampMixin:
    """
    Adds automatic creation and modification timestamps
    to database models.

    Models inheriting from this mixin automatically receive:

    - created_at
    - updated_at
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )