"""Health-check API endpoints."""

from datetime import UTC, datetime

from flask import Blueprint, jsonify


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    """Return the current backend health status."""

    return jsonify(
        {
            "application": "HomeLab Hub",
            "status": "ok",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )
