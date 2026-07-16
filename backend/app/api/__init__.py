"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     __init__.py

 Description:
     Registers all REST API blueprints used by the HomeLab Hub
     backend.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from flask import Flask

from .devices import devices_bp
from .health import health_bp


def register_api_blueprints(app: Flask) -> None:
    """
    Register every HomeLab Hub API blueprint.

    All API endpoints use the common ``/api`` URL prefix.

    Args:
        app:
            Configured Flask application instance.
    """

    app.register_blueprint(
        health_bp,
        url_prefix="/api",
    )

    app.register_blueprint(
        devices_bp,
        url_prefix="/api",
    )
