"""HomeLab Hub Flask application factory."""

from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template

from .api import register_api_blueprints
from .config import Config


def create_app() -> Flask:
    """Create and configure the HomeLab Hub Flask application."""

    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")

    app = Flask(
        __name__,
        instance_relative_config=True,
    )
    app.config.from_object(Config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    register_api_blueprints(app)

    @app.get("/")
    def index():
        """Render the initial HomeLab Hub landing page."""

        return render_template("index.html")

    return app
