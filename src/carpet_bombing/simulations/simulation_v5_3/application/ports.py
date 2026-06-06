"""Ports abstraits utilisés par la couche application.

Les services applicatifs dépendent de ces interfaces plutôt que de Mininet.
Une future infrastructure Containernet pourra donc fournir les mêmes ports.
"""

from pathlib import Path
from typing import Protocol, Sequence

from carpet_bombing.simulations.simulation_v5_3.domain.simulation_models import (
    SimulationConfig,
)


class ProcessRunner(Protocol):
    """Lance et arrête des processus longs dans un nœud réseau."""

    def start(
        self,
        node_name: str,
        arguments: Sequence[str],
        *,
        log_file: Path,
        timeout_seconds: int | None = None,
    ) -> None:
        """Lance un processus en arrière-plan."""

    def stop(self, node_name: str, process_pattern: str) -> None:
        """Arrête les processus correspondant au motif donné."""


class CommandRunner(Protocol):
    """Exécute des commandes courtes dans un nœud réseau."""

    def run(self, node_name: str, arguments: Sequence[str]) -> str:
        """Exécute une commande et retourne sa sortie textuelle."""


class Clock(Protocol):
    """Abstrait l'attente afin de tester les scénarios sans délai réel."""

    def sleep(self, seconds: float) -> None:
        """Attend pendant la durée demandée."""


class NetworkRuntime(Protocol):
    """Représente une topologie construite et son cycle de vie."""

    def start(self) -> None:
        """Démarre le réseau."""

    def stop(self) -> None:
        """Arrête le réseau et libère ses ressources."""


class TopologyBuilder(Protocol):
    """Construit une infrastructure réseau depuis la configuration du domaine."""

    def build(self, config: SimulationConfig) -> NetworkRuntime:
        """Construit et retourne un réseau qui n'est pas encore démarré."""


class InteractiveCli(Protocol):
    """Représente une interface interactive liée au réseau."""

    def run(self) -> None:
        """Démarre l'interface interactive."""
