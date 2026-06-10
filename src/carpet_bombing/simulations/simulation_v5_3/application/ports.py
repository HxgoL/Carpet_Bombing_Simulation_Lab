"""Interfaces utilisées par les services applicatifs.

Les Protocols définissent ce dont l'application a besoin sans imposer une
implémentation particulière. Les adaptateurs Mininet seront créés dans la
couche infrastructure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, Sequence


class ProcessRunner(Protocol):
    """Interface permettant d'exécuter des processus dans un nœud réseau."""

    def start(
        self,
        node_name: str,
        arguments: Sequence[str],
        *,
        log_file: Path,
        timeout_seconds: int | None = None,
    ) -> None:
        """Lance un processus en arrière-plan dans le nœud demandé."""

    def stop(self, node_name: str, process_pattern: str) -> None:
        """Arrête les processus correspondant au motif dans un nœud."""


class CommandRunner(Protocol):
    """Interface permettant d'exécuter une commande courte sur un nœud."""

    def run(self, node_name: str, arguments: Sequence[str]) -> str:
        """Exécute une commande et retourne sa sortie textuelle."""


class Clock(Protocol):
    """Interface abstraite utilisée pour contrôler le temps des scénarios."""

    def sleep(self, seconds: float) -> None:
        """Attend le nombre de secondes demandé."""


class SimulationNetwork(Protocol):
    """Interface minimale représentant le cycle de vie d'un réseau."""

    def start(self) -> None:
        """Démarre le réseau de simulation."""

    def stop(self) -> None:
        """Arrête le réseau et libère ses ressources."""


class TopologyBuilder(Protocol):
    """Interface permettant de construire un réseau depuis une configuration."""

    def build(self) -> SimulationNetwork:
        """Construit et retourne le réseau sans encore lancer les scénarios."""


class InteractiveCli(Protocol):
    """Interface représentant une console interactive de simulation."""

    def run(self) -> None:
        """Ouvre la console interactive et attend sa fermeture."""