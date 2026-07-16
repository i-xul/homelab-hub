"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     __init__.py

 Description:
     Registers the server-rendered web blueprint used by the
     HomeLab Hub browser interface.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from flask import Flask

from .routes import web_bp


def register_web_blueprints(app: Flask) -> None:
    """
    Register all browser-interface blueprints.

    Args:
        app:
            Configured Flask application instance.
    """

    app.register_blueprint(web_bp)
