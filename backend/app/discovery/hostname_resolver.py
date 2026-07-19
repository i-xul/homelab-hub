"""
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     hostname_resolver.py

 Description:
     Resolves hostnames for discovered network devices using
     multiple local name-resolution sources.

     The resolver currently tries the operating system resolver
     first and falls back to Avahi/mDNS when no useful hostname
     is available.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
"""

from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import shutil
import socket
import subprocess


class HostnameResolver:
    """
    Resolve human-readable hostnames for discovered IP addresses.

    Resolution sources are attempted in order so that standard
    local DNS remains the preferred source while mDNS can provide
    additional names for compatible devices.
    """

    def __init__(
        self,
        *,
        avahi_executable: str = "avahi-resolve-address",
        avahi_timeout_seconds: int = 2,
    ) -> None:
        """
        Initialize the hostname resolver.

        Args:
            avahi_executable:
                Name or path of the Avahi address resolver.

            avahi_timeout_seconds:
                Maximum time allowed for one mDNS lookup.
        """

        self._avahi_executable = shutil.which(avahi_executable)

        self._avahi_timeout_seconds = avahi_timeout_seconds

    def resolve(
        self,
        ip_address: str,
    ) -> str | None:
        """
        Resolve one IP address into the best available hostname.

        Resolution order:

        1. Operating system resolver / reverse DNS.
        2. Avahi / mDNS.

        Args:
            ip_address:
                IPv4 or IPv6 address to resolve.

        Returns:
            Resolved hostname, or None when no useful name can be
            determined.
        """

        hostname = self._resolve_system(ip_address)

        if hostname is not None:
            return hostname

        return self._resolve_avahi(ip_address)

    def resolve_many(
        self,
        ip_addresses: list[str],
        *,
        max_workers: int = 8,
    ) -> dict[str, str]:
        """
        Resolve multiple IP addresses concurrently.

        Parallel resolution prevents slow or unanswered mDNS
        lookups from significantly delaying a complete network
        scan.

        Args:
            ip_addresses:
                Addresses that require hostname resolution.

            max_workers:
                Maximum number of simultaneous resolver tasks.

        Returns:
            Mapping containing only addresses for which a useful
            hostname was successfully resolved.

        Raises:
            ValueError:
                If max_workers is less than one.
        """

        if max_workers < 1:
            raise ValueError("max_workers must be at least one.")

        unique_addresses = list(dict.fromkeys(ip_addresses))

        if not unique_addresses:
            return {}

        resolved_hostnames: dict[str, str] = {}

        with ThreadPoolExecutor(
            max_workers=max_workers,
        ) as executor:
            future_to_ip = {
                executor.submit(
                    self.resolve,
                    ip_address,
                ): ip_address
                for ip_address in unique_addresses
            }

            for future in as_completed(future_to_ip):
                ip_address = future_to_ip[future]

                try:
                    hostname = future.result()
                except Exception:
                    # One failed resolver task must not abort the
                    # complete network discovery cycle.
                    continue

                if hostname is not None:
                    resolved_hostnames[ip_address] = hostname

        return resolved_hostnames

    @staticmethod
    def _normalize_hostname(
        hostname: str,
        ip_address: str,
    ) -> str | None:
        """
        Normalize a hostname returned by a resolver.

        Args:
            hostname:
                Raw hostname returned by a resolver.

            ip_address:
                Original address being resolved.

        Returns:
            Clean hostname, or None when the value is not useful.
        """

        normalized_hostname = hostname.strip().rstrip(".")

        if not normalized_hostname:
            return None

        if normalized_hostname == ip_address:
            return None

        return normalized_hostname

    def _resolve_system(
        self,
        ip_address: str,
    ) -> str | None:
        """
        Resolve a hostname using the operating system resolver.

        Args:
            ip_address:
                Address to resolve.

        Returns:
            Resolved hostname, or None.
        """

        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
        except (
            socket.herror,
            socket.gaierror,
            OSError,
        ):
            return None

        return self._normalize_hostname(
            hostname,
            ip_address,
        )

    def _resolve_avahi(
        self,
        ip_address: str,
    ) -> str | None:
        """
        Resolve a hostname using Avahi/mDNS.

        Args:
            ip_address:
                Address to resolve.

        Returns:
            Resolved mDNS hostname, or None when Avahi is not
            installed or no device responds.
        """

        if self._avahi_executable is None:
            return None

        command = [
            self._avahi_executable,
            ip_address,
        ]

        try:
            completed_process = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
                timeout=self._avahi_timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return None

        if completed_process.returncode != 0:
            return None

        output = completed_process.stdout.strip()

        if not output:
            return None

        parts = output.split()

        if len(parts) < 2:
            return None

        return self._normalize_hostname(
            parts[-1],
            ip_address,
        )
