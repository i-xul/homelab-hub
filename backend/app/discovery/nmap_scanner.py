"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     nmap_scanner.py

 Description:
     Implements local-network discovery by running the Nmap
     command-line tool and parsing its XML output.

     The scanner returns temporary DiscoveredDevice objects.
     It does not write directly to the database.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations

import ipaddress
import shutil
import subprocess
import xml.etree.ElementTree as ElementTree

from .models import DiscoveredDevice
from .scanner import DiscoveryError
from app.settings import NMAP_TIMEOUT_SECONDS


class NmapScanner:
    """
    Discover network devices by using an Nmap ping scan.

    Nmap XML output is used instead of human-readable terminal
    output because XML provides a stable and structured format
    for extracting host information.

    The scanner performs discovery only. Database updates are
    handled separately by the application service layer.
    """

    def __init__(
        self,
        *,
        executable: str = "nmap",
        timeout_seconds: int = NMAP_TIMEOUT_SECONDS,
    ) -> None:
        """
        Initialize the Nmap scanner.

        Args:
            executable:
                Name or absolute path of the Nmap executable.

            timeout_seconds:
                Maximum time allowed for one scan before the
                subprocess is terminated.

        Raises:
            DiscoveryError:
                If the Nmap executable cannot be located.
        """

        executable_path = shutil.which(executable)

        if executable_path is None:
            raise DiscoveryError(f"Nmap executable was not found: {executable}")

        self._executable = executable_path
        self._timeout_seconds = timeout_seconds

    def scan(self, network: str) -> list[DiscoveredDevice]:
        """
        Scan a network and return all hosts reported as online.

        Args:
            network:
                IPv4 or IPv6 network in CIDR notation, such as
                ``192.168.1.0/24``.

        Returns:
            List of detected devices sorted by IP address.

        Raises:
            DiscoveryError:
                If the network value is invalid, Nmap fails,
                the scan times out or XML parsing fails.
        """

        validated_network = self._validate_network(network)

        command = [
            self._executable,
            "-sn",
            "-oX",
            "-",
            str(validated_network),
        ]

        try:
            completed_process = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
                timeout=self._timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            raise DiscoveryError(
                f"Nmap scan exceeded the {self._timeout_seconds}-second timeout."
            ) from error
        except OSError as error:
            raise DiscoveryError(f"Nmap could not be started: {error}") from error

        if completed_process.returncode != 0:
            error_message = completed_process.stderr.strip()

            raise DiscoveryError(
                "Nmap scan failed" + (f": {error_message}" if error_message else ".")
            )

        return self._parse_xml(completed_process.stdout)

    @staticmethod
    def _validate_network(
        network: str,
    ) -> ipaddress.IPv4Network | ipaddress.IPv6Network:
        """
        Validate and normalize a network target.

        Strict mode is disabled so that an address such as
        ``192.168.1.15/24`` is normalized to
        ``192.168.1.0/24``.

        Args:
            network:
                Network or host address with a CIDR prefix.

        Returns:
            Parsed IPv4Network or IPv6Network instance.

        Raises:
            DiscoveryError:
                If the supplied value is not valid CIDR input.
        """

        try:
            return ipaddress.ip_network(
                network.strip(),
                strict=False,
            )
        except ValueError as error:
            raise DiscoveryError(f"Invalid network target: {network}") from error

    @staticmethod
    def _parse_xml(xml_output: str) -> list[DiscoveredDevice]:
        """
        Convert Nmap XML output into discovery data objects.

        Hosts not marked as online are ignored. MAC address,
        hostname and manufacturer values remain optional
        because Nmap cannot always determine them.

        Args:
            xml_output:
                Complete XML document produced by Nmap.

        Returns:
            Parsed devices sorted by their IP addresses.

        Raises:
            DiscoveryError:
                If the XML document cannot be parsed.
        """

        try:
            root = ElementTree.fromstring(xml_output)
        except ElementTree.ParseError as error:
            raise DiscoveryError("Nmap returned invalid XML output.") from error

        discovered_devices: list[DiscoveredDevice] = []

        for host_element in root.findall("host"):
            status_element = host_element.find("status")

            if status_element is None or status_element.get("state") != "up":
                continue

            addresses = {
                address.get("addrtype"): address
                for address in host_element.findall("address")
            }

            # ElementTree elements without child elements may
            # evaluate as False even when they exist. Select the
            # address explicitly instead of using boolean "or".
            network_address = addresses.get("ipv4")

            if network_address is None:
                network_address = addresses.get("ipv6")

            if network_address is None:
                continue

            mac_element = addresses.get("mac")
            hostname_element = host_element.find("hostnames/hostname")

            discovered_devices.append(
                DiscoveredDevice(
                    ip_address=network_address.get("addr", ""),
                    mac_address=(
                        mac_element.get("addr", "").lower()
                        if mac_element is not None
                        else None
                    ),
                    hostname=(
                        hostname_element.get("name")
                        if hostname_element is not None
                        else None
                    ),
                    manufacturer=(
                        mac_element.get("vendor") if mac_element is not None else None
                    ),
                )
            )

        return sorted(
            discovered_devices,
            key=lambda device: ipaddress.ip_address(device.ip_address),
        )
