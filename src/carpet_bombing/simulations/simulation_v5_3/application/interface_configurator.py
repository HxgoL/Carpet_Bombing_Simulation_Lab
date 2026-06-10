"""Service applicatif configurant les adresses des interfaces réseau."""

from __future__ import annotations

from collections.abc import Iterable

from carpet_bombing.simulations.simulation_v5_3.application.ports import (
    CommandRunner,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    LinkSpec,
)


class InterfaceConfigurator:
    """Applique les adresses déclarées sur les extrémités des liens."""

    def __init__(self, command_runner: CommandRunner) -> None:
        """Initialise le configurateur avec son adaptateur de commandes."""

        self._command_runner = command_runner

    def configure(self, links: Iterable[LinkSpec]) -> None:
        """Configure toutes les adresses d'interfaces décrites par les liens."""

        for link in links:
            self._configure_endpoint(
                link.left_node,
                link.left_interface,
                link.left_ip_cidr,
            )
            self._configure_endpoint(
                link.right_node,
                link.right_interface,
                link.right_ip_cidr,
            )

    def _configure_endpoint(
        self,
        node_name: str,
        interface_name: str | None,
        ip_cidr: str | None,
    ) -> None:
        """Configure une extrémité uniquement lorsqu'elle possède une adresse."""

        if interface_name is None or ip_cidr is None:
            return

        self._command_runner.run(
            node_name,
            [
                "ip",
                "link",
                "set",
                "dev",
                interface_name,
                "up",
            ],
        )
        self._command_runner.run(
            node_name,
            [
                "ip",
                "address",
                "replace",
                ip_cidr,
                "dev",
                interface_name,
            ],
        )
