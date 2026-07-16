"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     settings.py

 Description:
     Defines configurable application settings used by
     HomeLab Hub.

     These values represent installation-specific behaviour
     that may later be loaded from environment variables,
     configuration files or the web interface.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

import os


# ---------------------------------------------------------
# Network discovery
# ---------------------------------------------------------

# Default network scanned by HomeLab Hub.
#
# The value must use CIDR notation, for example:
# 192.168.1.0/24
DEFAULT_NETWORK = os.getenv(
    "HOMELAB_HUB_NETWORK",
    "192.168.1.0/24",
)

# Time between automatic network scans.
SCAN_INTERVAL_SECONDS = int(
    os.getenv(
        "HOMELAB_HUB_SCAN_INTERVAL",
        "300",
    )
)

# Number of consecutive missed scans required before an online
# device is considered offline.
OFFLINE_SCAN_THRESHOLD = int(
    os.getenv(
        "HOMELAB_HUB_OFFLINE_THRESHOLD",
        "3",
    )
)


# ---------------------------------------------------------
# Discovery subprocess
# ---------------------------------------------------------

# Maximum time allowed for an individual Nmap scan.
NMAP_TIMEOUT_SECONDS = int(
    os.getenv(
        "HOMELAB_HUB_NMAP_TIMEOUT",
        "120",
    )
)