"""Service applicatif responsable de la configuration des routes."""

from __future__ import annotations

from collections.abc import Iterable

from carpet_bombing.simulations.simulation_v5_3.application.ports import (
    CommandRunner,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    RouteSpec,
)


class RouteConfigurator:
    """Traduit des descriptions de routes en commandes Linux."""

    def __init__(self, command_runner: CommandRunner) -> None:
        """Initialise le configurateur avec son adaptateur de commandes."""
        self._command_runner = command_runner

    def configure(self, routes: Iterable[RouteSpec]) -> None:
        """Configure toutes les routes fournies."""
        for route in routes:
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
