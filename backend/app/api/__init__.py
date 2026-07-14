"""API blueprint registration."""

from flask import Flask

from .health import health_bp


def register_api_blueprints(app: Flask) -> None:
    """Register all API blueprints with the Flask application."""

    app.register_blueprint(health_bp, url_prefix="/api")
