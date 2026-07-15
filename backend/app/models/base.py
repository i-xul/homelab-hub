"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     base.py

 Description:
     Defines the declarative SQLAlchemy base class used by
     every database model in HomeLab Hub.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for every SQLAlchemy model.

    All database models should inherit from this class.
    """

    pass