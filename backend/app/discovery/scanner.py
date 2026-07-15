"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     scanner.py

 Description:
     Defines the common interface used by HomeLab Hub network
     discovery implementations.

     Concrete scanners may later use Nmap, operating-system
     neighbour tables or other discovery methods without
     changing the service layer that consumes their results.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

from typing import Protocol

from .models import DiscoveredDevice


class NetworkScanner(Protocol):
    """
    Define the interface required from network scanners.

    Any scanner implementing a compatible scan() method can
    be used by HomeLab Hub without inheriting from this class.
    This keeps the discovery layer lightweight and makes it
    straightforward to provide alternative scanners in tests.
    """

    def scan(self, network: str) -> list[DiscoveredDevice]:
        """
        Scan the supplied network and return detected devices.

        Args:
            network:
                Network target in CIDR notation, for example
                ``192.168.1.0/24``.

        Returns:
            List of devices detected during the completed scan.

        Raises:
            DiscoveryError:
                If the scanner cannot complete the operation.
        """

        ...


class DiscoveryError(RuntimeError):
    """
    Represent a failure reported by a network scanner.

    Scanner implementations should translate tool-specific
    failures into this exception so that callers do not need
    to understand the details of Nmap or another scan method.
    """