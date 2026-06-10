"""Adaptateurs permettant d'exécuter des commandes dans les nœuds Mininet."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Sequence

from mininet.net import Mininet
from mininet.node import Node


class MininetCommandRunner:
    """Exécute des commandes courtes dans les nœuds Mininet."""

    def __init__(self, network: Mininet) -> None:
        """Conserve une référence vers le réseau Mininet."""
        self._network = network

    def run(self, node_name: str, arguments: Sequence[str]) -> str:
        """Exécute une commande et retourne sa sortie textuelle."""
        node = self._get_node(node_name)
        command = _build_shell_command(arguments)

        return str(node.cmd(command))

    def _get_node(self, node_name: str) -> Node:
        """Retourne un nœud Mininet à partir de son nom."""
        return self._network.get(node_name)


class MininetProcessRunner:
    """Lance et arrête des processus dans les nœuds Mininet."""

    def __init__(self, network: Mininet) -> None:
        """Conserve une référence vers le réseau Mininet."""
        self._network = network

    def start(
        self,
        node_name: str,
        arguments: Sequence[str],
        *,
        log_file: Path,
        timeout_seconds: int | None = None,
    ) -> None:
        """Lance un processus en arrière-plan dans un nœud."""
        node = self._get_node(node_name)
        command = _build_shell_command(arguments)

        if timeout_seconds is not None:
            command = f"timeout {timeout_seconds} {command}"

        quoted_log_file = shlex.quote(str(log_file))
        background_command = f"{command} > {quoted_log_file} 2>&1 &"

        node.cmd(background_command)

    def stop(self, node_name: str, process_pattern: str) -> None:
        """Arrête les processus correspondant au motif fourni."""
        node = self._get_node(node_name)
        quoted_pattern = shlex.quote(process_pattern)

        node.cmd(f"pkill -f -- {quoted_pattern} || true")

    def _get_node(self, node_name: str) -> Node:
        """Retourne un nœud Mininet à partir de son nom."""
        return self._network.get(node_name)


def _build_shell_command(arguments: Sequence[str]) -> str:
    """Construit une commande shell en protégeant chaque argument."""
    if not arguments:
        raise ValueError("A command must contain at least one argument.")

    return shlex.join(arguments)
