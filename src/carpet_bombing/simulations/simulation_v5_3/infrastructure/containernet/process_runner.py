"""Adaptateurs exécutant des commandes dans les nœuds Containernet."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Sequence

from mininet.net import Containernet
from mininet.node import Node


class ContainernetCommandRunner:
    """Exécute des commandes courtes dans les hôtes et conteneurs."""

    def __init__(self, network: Containernet) -> None:
        """Conserve une référence vers le réseau Containernet."""

        self._network = network

    def run(self, node_name: str, arguments: Sequence[str]) -> str:
        """Exécute une commande et retourne sa sortie textuelle."""

        node = self._get_node(node_name)
        return str(node.cmd(_build_shell_command(arguments)))

    def _get_node(self, node_name: str) -> Node:
        """Retourne un nœud Containernet à partir de son nom."""

        return self._network.get(node_name)


class ContainernetProcessRunner:
    """Lance et arrête des processus dans les hôtes et conteneurs."""

    def __init__(self, network: Containernet) -> None:
        """Conserve une référence vers le réseau Containernet."""

        self._network = network

    def start(
        self,
        node_name: str,
        arguments: Sequence[str],
        *,
        log_file: Path,
        timeout_seconds: int | None = None,
    ) -> None:
        """Lance un processus en arrière-plan dans le nœud demandé."""

        node = self._get_node(node_name)
        command = _build_shell_command(arguments)

        if timeout_seconds is not None:
            command = f"timeout {timeout_seconds} {command}"

        quoted_log_file = shlex.quote(str(log_file))
        node.cmd(f"{command} > {quoted_log_file} 2>&1 &")

    def stop(self, node_name: str, process_pattern: str) -> None:
        """Arrête les processus correspondant au motif fourni."""

        node = self._get_node(node_name)
        quoted_pattern = shlex.quote(process_pattern)
        node.cmd(f"pkill -f -- {quoted_pattern} || true")

    def _get_node(self, node_name: str) -> Node:
        """Retourne un nœud Containernet à partir de son nom."""

        return self._network.get(node_name)


def _build_shell_command(arguments: Sequence[str]) -> str:
    """Construit une commande shell en protégeant chaque argument."""

    if not arguments:
        raise ValueError("A command must contain at least one argument.")

    return shlex.join(arguments)
