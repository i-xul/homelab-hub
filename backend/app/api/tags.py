"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     tags.py

 Description:
     Provides REST API endpoints for managing HomeLab Hub
     inventory tags and device tag assignments.

     The API keeps HTTP request handling separate from tag
     database operations implemented by the service layer.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from typing import Any

from flask import Blueprint
from flask import jsonify
from flask import request

from app.database import SessionLocal
from app.models import Tag
from app.services import assign_tag_to_device
from app.services import create_tag
from app.services import get_all_tags
from app.services import get_device_by_id
from app.services import get_tag_by_id
from app.services import remove_tag_from_device


tags_bp = Blueprint(
    "tags",
    __name__,
)


# ---------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------


def _serialize_tag(
    tag: Tag,
) -> dict[str, Any]:
    """
    Convert a Tag database model into API-safe JSON data.

    Args:
        tag:
            Tag instance to serialize.

    Returns:
        Dictionary containing public inventory tag data.
    """

    return {
        "id": tag.id,
        "name": tag.name,
        "color": tag.color,
    }


# ---------------------------------------------------------
# Tag endpoints
# ---------------------------------------------------------


@tags_bp.get("/tags")
def list_tags():
    """
    Return every inventory tag.

    Tags are ordered alphabetically by the service layer.

    Returns:
        HTTP 200 with the complete tag list.
    """

    with SessionLocal() as database_session:
        tags = get_all_tags(database_session)

        serialized_tags = [
            _serialize_tag(tag)
            for tag in tags
        ]

    return jsonify(
        {
            "tags": serialized_tags,
        }
    )


@tags_bp.post("/tags")
def add_tag():
    """
    Create a new inventory tag.

    Request JSON must contain a tag name. An optional color may
    also be supplied.

    Returns:
        HTTP 201 with the newly created tag on success.

        HTTP 400 when request data is invalid or the tag already
        exists.
    """

    payload = request.get_json(
        silent=True,
    )

    if not isinstance(payload, dict):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Request body must contain a JSON object.",
                }
            ),
            400,
        )

    allowed_fields = {
        "name",
        "color",
    }

    unexpected_fields = set(payload) - allowed_fields

    if unexpected_fields:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": (
                        "Unsupported fields: "
                        + ", ".join(sorted(unexpected_fields))
                    ),
                }
            ),
            400,
        )

    name = payload.get("name")

    if not isinstance(name, str):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "name must be a string.",
                }
            ),
            400,
        )

    color = payload.get("color")

    if color is not None and not isinstance(
        color,
        str,
    ):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "color must be a string or null.",
                }
            ),
            400,
        )

    with SessionLocal() as database_session:
        try:
            tag = create_tag(
                database_session,
                name=name,
                color=color,
            )
        except ValueError as error:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": str(error),
                    }
                ),
                400,
            )

        response_data = _serialize_tag(tag)

    return (
        jsonify(
            {
                "status": "created",
                "tag": response_data,
            }
        ),
        201,
    )


# ---------------------------------------------------------
# Device tag assignment endpoints
# ---------------------------------------------------------


@tags_bp.post(
    "/devices/<int:device_id>/tags/<int:tag_id>"
)
def add_device_tag(
    device_id: int,
    tag_id: int,
):
    """
    Assign an existing tag to an inventory device.

    Args:
        device_id:
            Database identifier of the target device.

        tag_id:
            Database identifier of the tag to assign.

    Returns:
        HTTP 200 with the assigned tag on success.

        HTTP 404 when either the device or tag does not exist.
    """

    with SessionLocal() as database_session:
        device = get_device_by_id(
            database_session,
            device_id,
        )

        if device is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Device not found.",
                    }
                ),
                404,
            )

        tag = get_tag_by_id(
            database_session,
            tag_id,
        )

        if tag is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Tag not found.",
                    }
                ),
                404,
            )

        assign_tag_to_device(
            database_session,
            device,
            tag,
        )

        response_data = _serialize_tag(tag)

    return jsonify(
        {
            "status": "assigned",
            "tag": response_data,
        }
    )


@tags_bp.delete(
    "/devices/<int:device_id>/tags/<int:tag_id>"
)
def delete_device_tag(
    device_id: int,
    tag_id: int,
):
    """
    Remove a tag assignment from an inventory device.

    The tag itself remains available for assignment to other
    devices.

    Args:
        device_id:
            Database identifier of the target device.

        tag_id:
            Database identifier of the tag to remove.

    Returns:
        HTTP 200 after the assignment has been removed.

        HTTP 404 when either the device or tag does not exist.
    """

    with SessionLocal() as database_session:
        device = get_device_by_id(
            database_session,
            device_id,
        )

        if device is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Device not found.",
                    }
                ),
                404,
            )

        tag = get_tag_by_id(
            database_session,
            tag_id,
        )

        if tag is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Tag not found.",
                    }
                ),
                404,
            )

        remove_tag_from_device(
            database_session,
            device,
            tag,
        )

        response_data = _serialize_tag(tag)

    return jsonify(
        {
            "status": "removed",
            "tag": response_data,
        }
    )