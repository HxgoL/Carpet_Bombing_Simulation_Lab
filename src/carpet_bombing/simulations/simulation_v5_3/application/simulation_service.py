"""Façade coordonnant le cycle de vie complet d'une simulation."""

from __future__ import annotations

from carpet_bombing.simulations.simulation_v5_3.application.attack_service import (
    AttackService,
)
from carpet_bombing.simulations.simulation_v5_3.application.interface_configurator import (
    InterfaceConfigurator,
)
from carpet_bombing.simulations.simulation_v5_3.application.ports import (
    InteractiveCli,
    SimulationNetwork,
)
from carpet_bombing.simulations.simulation_v5_3.application.route_configurator import (
    RouteConfigurator,
)
from carpet_bombing.simulations.simulation_v5_3.application.scenario_runner import (
    ScenarioRunner,
)
from carpet_bombing.simulations.simulation_v5_3.application.traffic_service import (
    TrafficService,
)
from carpet_bombing.simulations.simulation_v5_3.domain.simulation_models import (
    SimulationConfig,
)


class SimulationService:
    """Fournit un point d'entrée unique pour piloter la simulation."""

    def __init__(
        self,
        config: SimulationConfig,
        network: SimulationNetwork,
        interface_configurator: InterfaceConfigurator,
        route_configurator: RouteConfigurator,
        traffic_service: TrafficService,
        attack_service: AttackService,
        scenario_runner: ScenarioRunner,
        interactive_cli: InteractiveCli,
    ) -> None:
        """Initialise la façade avec tous les composants nécessaires."""

        self._config = config
        self._network = network
        self._interface_configurator = interface_configurator
        self._route_configurator = route_configurator
        self._traffic_service = traffic_service
        self._attack_service = attack_service
        self._scenario_runner = scenario_runner
        self._interactive_cli = interactive_cli

        self._network_started = False
        self._closed = False

    def run(self) -> None:
        """Démarre et exécute la simulation configurée."""

        try:
            self._start_network()
            self._interface_configurator.configure(self._config.links)
            self._route_configurator.configure(self._config.routes)
            self._traffic_service.start()
            self._print_summary()
            self._run_selected_mode()
        finally:
            self.close()

    def close(self) -> None:
        """Nettoie les ressources de manière idempotente."""

        if self._closed:
            return

        self._closed = True

        if not self._network_started:
            return

        try:
            self._attack_service.stop()
        finally:
            try:
                self._traffic_service.stop()
            finally:
                self._network.stop()
                self._network_started = False

    def _start_network(self) -> None:
        """Démarre le réseau et mémorise son état."""

        self._network.start()
        self._network_started = True

    def _run_selected_mode(self) -> None:
        """Lance un scénario automatique ou la CLI interactive."""

        scenario_name = self._config.scenario.name

        if scenario_name is None:
            self._interactive_cli.run()
            return

        self._scenario_runner.run(scenario_name)

    def _print_summary(self) -> None:
        """Affiche les informations utiles avant le scénario."""

        attack = self._config.attack
        containerized_victims = sum(
            victim.is_containerized
            for victim in self._config.victims
        )

        print("\nSimulation V5.3 : topologie multi-routeurs")
        print("  Scénarios : normal, single_target, carpet")
        print("  Chemin : attaquants -> r1/r2 -> r_core -> gw -> victimes")
        print(f"  Nombre d'attaquants : {len(self._config.attackers)}")
        print(f"  Nombre de victimes actives : {len(self._config.victims)}")
        print(f"  Victimes conteneurisées : {containerized_victims}")
        print(f"  Cible single-target : {self._config.single_target_ip}")
        print(
            f"  Attaque : {attack.packets_per_second} pps, "
            f"protocole {attack.protocol}, "
            f"fragmentation {attack.fragment_mode}"
        )
        print()
