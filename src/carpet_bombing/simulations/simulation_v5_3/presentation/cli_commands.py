"""Console Mininet enrichie avec les commandes de la simulation."""

from __future__ import annotations

from mininet.cli import CLI
from mininet.net import Mininet

from carpet_bombing.simulations.simulation_v5_3.application.attack_service import (
    AttackService,
)


class SimulationCli(CLI):
    """CLI Mininet proposant des commandes de gestion des attaques."""

    def __init__(
        self,
        network: Mininet,
        attack_service: AttackService,
    ) -> None:
        """Initialise les services avant d'ouvrir la CLI Mininet."""

        self._attack_service = attack_service
        super().__init__(network)

    def do_start_single_target_attack(self, _line: str) -> None:
        """Lance une attaque concentrée sur la victime principale."""

        self._attack_service.launch_single_target()
        print("Attaque single-target V5.3 lancée")

    def do_start_carpet_attack(self, _line: str) -> None:
        """Lance une attaque carpet bombing."""

        self._attack_service.launch_carpet()
        print("Attaque carpet bombing V5.3 lancée")

    def do_stop_attack(self, _line: str) -> None:
        """Arrête toutes les attaques actives."""

        self._attack_service.stop()
        print("Attaque V5.3 arrêtée")


class MininetInteractiveCli:
    """Adaptateur ouvrant la CLI interactive de la simulation."""

    def __init__(
        self,
        network: Mininet,
        attack_service: AttackService,
    ) -> None:
        """Conserve les dépendances nécessaires à la CLI."""

        self._network = network
        self._attack_service = attack_service

    def run(self) -> None:
        """Ouvre la CLI et attend sa fermeture."""

        self._print_available_commands()
        SimulationCli(self._network, self._attack_service)

    def _print_available_commands(self) -> None:
        """Affiche les commandes spécifiques disponibles."""

        print("\nCommandes de test :")
        print("  a1 traceroute 10.0.0.1")
        print("  start_single_target_attack")
        print("  start_carpet_attack")
        print("  stop_attack")
        print("  gw tc -s qdisc show dev gw-eth1")
        print()