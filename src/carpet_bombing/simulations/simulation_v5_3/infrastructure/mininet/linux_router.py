"""Implémentation Mininet d'un routeur Linux."""

from __future__ import annotations

from typing import Any

from mininet.node import Node


class LinuxRouter(Node):
    """Nœud Mininet capable de transférer des paquets IPv4."""

    def config(self, **params: Any) -> None:
        """Configure le nœud puis active le routage IPv4."""
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self) -> None:
        """Désactive le routage IPv4 puis arrête le nœud."""
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()
