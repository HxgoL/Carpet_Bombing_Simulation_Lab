"""Service applicatif chargé d'installer les routes statiques."""

from collections.abc import Iterable

from carpet_bombing.simulations.simulation_v5_3.application.ports import (
    CommandRunner,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    RouteSpec,
)


class RouteConfigurator:
    """Traduit les routes du domaine en commandes Linux."""

    def __init__(self, command_runner: CommandRunner) -> None:
        self._command_runner = command_runner

    def configure(self, routes: Iterable[RouteSpec]) -> None:
        """Installe chaque route sur le nœud correspondant."""

        for route in routes:
            self._command_runner.run(
                route.node_name,
                (
                    "ip",
                    "route",
                    "replace",
                    route.destination,
                    "via",
                    route.gateway,
                ),
            )
