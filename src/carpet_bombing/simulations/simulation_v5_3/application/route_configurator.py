"""Service applicatif responsable de la configuration des routes."""

from __future__ import annotations

from carpet_bombing.simulations.simulation_v5_3.application.ports import (
    CommandRunner,
)
from carpet_bombing.simulations.simulation_v5_3.domain.models import (
    SimulationConfig,
)

# Le RouteConfigurator est responsable de configurer les routes dans les nœuds
class RouteConfigurator:

    """Initialise le configurateur avec ses dépendances."""
    def __init__(
        self,
        config: SimulationConfig,
        command_runner: CommandRunner,
    ) -> None:

        self._config = config
        self._command_runner = command_runner

    """Configure toutes les routes nécessaires à la simulation."""
    def configure(self) -> None:

        self._configure_attacker_default_routes()
        self._configure_victim_default_routes()
        self._configure_static_routes()


    def _configure_attacker_default_routes(self) -> None:
        """Configure la route par défaut de chaque attaquant."""

        for attacker in self._config.attackers:
            self._command_runner.run(
                attacker.name,
                [
                    "ip",
                    "route",
                    "replace",
                    "default",
                    "via",
                    attacker.gateway,
                ],
            )

    def _configure_victim_default_routes(self) -> None:
        """Configure la route par défaut de chaque victime."""

        for victim in self._config.victims:
            self._command_runner.run(
                victim.name,
                [
                    "ip",
                    "route",
                    "replace",
                    "default",
                    "via",
                    victim.gateway,
                ],
            )

    def _configure_static_routes(self) -> None:
        """Configure les routes statiques des routeurs."""

        for route in self._config.routes:
            self._command_runner.run(
                route.node_name,
                [
                    "ip",
                    "route",
                    "replace",
                    route.destination,
                    "via",
                    route.gateway,
                ],
            )