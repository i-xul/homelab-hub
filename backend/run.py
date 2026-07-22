"""Development entry point for HomeLab Hub."""

import os

from app import create_app
from app.services import InventoryScanScheduler


app = create_app()


if __name__ == "__main__":
    host = os.getenv("HOMELAB_HUB_HOST", "127.0.0.1")
    port = int(os.getenv("HOMELAB_HUB_PORT", "5000"))

    scheduler = InventoryScanScheduler()

    app.extensions["inventory_scan_scheduler"] = scheduler

    # Flask's debug reloader starts a parent monitoring process
    # and a separate child process that serves the application.
    # Start the scheduler only inside the serving process.
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler.start()

    try:
        app.run(
            host=host,
            port=port,
            debug=True,
        )
    finally:
        scheduler.stop()
