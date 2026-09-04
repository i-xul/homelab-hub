"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     tag_service.py

 Description:
     Provides database operations for creating, retrieving and
     assigning user-managed inventory tags.

     This service layer keeps tag database logic separate from
     API endpoints and user-interface code.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Device
from app.models import Tag


# ---------------------------------------------------------
# Tag lookup
# ---------------------------------------------------------


def get_tag_by_id(
    database_session: Session,
    tag_id: int,
) -> Tag | None:
    """
    Return a tag matching the supplied database identifier.

    Args:
        database_session:
            Active SQLAlchemy database session.

        tag_id:
            Database identifier of the tag.

    Returns:
        Matching Tag instance, or None when no tag exists.
    """

    return database_session.get(
        Tag,
        tag_id,
    )


def get_tag_by_name(
    database_session: Session,
    name: str,
) -> Tag | None:
    """
    Return a tag matching the supplied name.

    Tag lookup is case-insensitive so that names such as
    "Linux" and "linux" refer to the same logical tag.

    Args:
        database_session:
            Active SQLAlchemy database session.

        name:
            Tag name to search for.

    Returns:
        Matching Tag instance, or None when no tag exists.
    """

    normalized_name = name.strip()

    if not normalized_name:
        return None

    statement = select(Tag).where(
        func.lower(Tag.name) == normalized_name.lower()
    )

    return database_session.scalar(statement)


def get_all_tags(
    database_session: Session,
) -> list[Tag]:
    """
    Return every tag stored in the inventory.

    Tags are ordered alphabetically by name to provide
    predictable output for the API and user interface.

    Args:
        database_session:
            Active SQLAlchemy database session.

    Returns:
        Alphabetically ordered list of Tag instances.
    """

    statement = select(Tag).order_by(
        func.lower(Tag.name),
        Tag.id,
    )

    return list(database_session.scalars(statement).all())


# ---------------------------------------------------------
# Tag creation
# ---------------------------------------------------------


def create_tag(
    database_session: Session,
    *,
    name: str,
    color: str | None = None,
) -> Tag:
    """
    Create and persist a new inventory tag.

    Tag names are stripped of surrounding whitespace and must
    be unique regardless of letter case.

    Args:
        database_session:
            Active SQLAlchemy database session.

        name:
            User-defined tag name.

        color:
            Optional user-defined display color.

    Returns:
        Newly created and persisted Tag instance.

    Raises:
        ValueError:
            If the tag name is empty or a tag with the same
            case-insensitive name already exists.
    """

    normalized_name = name.strip()

    if not normalized_name:
        raise ValueError("Tag name must not be empty.")

    existing_tag = get_tag_by_name(
        database_session,
        normalized_name,
    )

    if existing_tag is not None:
        raise ValueError(
            f"Tag already exists with name {existing_tag.name}."
        )

    normalized_color = None

    if color is not None:
        stripped_color = color.strip()
        normalized_color = stripped_color if stripped_color else None

    tag = Tag(
        name=normalized_name,
        color=normalized_color,
    )

    database_session.add(tag)
    database_session.commit()
    database_session.refresh(tag)

    return tag


# ---------------------------------------------------------
# Device tag assignment
# ---------------------------------------------------------


def assign_tag_to_device(
    database_session: Session,
    device: Device,
    tag: Tag,
) -> Device:
    """
    Assign an existing tag to an inventory device.

    Reassigning a tag that is already attached to the device
    is treated as a no-op.

    Args:
        database_session:
            Active SQLAlchemy database session.

        device:
            Device receiving the tag.

        tag:
            Tag to assign.

    Returns:
        Updated and persisted Device instance.
    """

    if tag not in device.tags:
        device.tags.append(tag)

        database_session.commit()
        database_session.refresh(device)

    return device


def remove_tag_from_device(
    database_session: Session,
    device: Device,
    tag: Tag,
) -> Device:
    """
    Remove an assigned tag from an inventory device.

    Removing a tag that is not currently attached to the
    device is treated as a no-op.

    Args:
        database_session:
            Active SQLAlchemy database session.

        device:
            Device from which the tag should be removed.

        tag:
            Tag to remove.

    Returns:
        Updated and persisted Device instance.
    """

    if tag in device.tags:
        device.tags.remove(tag)

        database_session.commit()
        database_session.refresh(device)

    return device