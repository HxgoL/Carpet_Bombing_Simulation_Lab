"""Builder construisant la topologie V5.3 avec Containernet."""

from __future__ import annotations

from typing import Any

from containernet.net import Containernet
from mininet.link import TCLink
from mininet.node import OVSBridge

from carpet_bombing.simulations.simulation_v5_3.domain.simulation_models import (
    SimulationConfig,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    LinkSpec,
    VictimSpec,
)
from carpet_bombing.simulations.simulation_v5_3.infrastructure.containernet.docker_host import (
    build_add_docker_options,
)
from carpet_bombing.simulations.simulation_v5_3.infrastructure.containernet.linux_router import (
    LinuxRouter,
)


class ContainernetTopologyBuilder:
    """Construit un réseau où les victimes sont des conteneurs Docker."""

    def __init__(self, config: SimulationConfig) -> None:
        """Conserve et valide la configuration à construire."""

        self._config = config

        non_containerized = [
            victim.name
            for victim in config.victims
            if not victim.is_containerized
        ]

        if non_containerized:
            raise ValueError(
                "Containernet requires containerized victims: "
                + ", ".join(non_containerized)
            )

    def build(self) -> Containernet:
        """Construit et retourne un réseau Containernet non démarré."""

        network = Containernet(
            controller=None,
            switch=OVSBridge,
            link=TCLink,
        )

        self._add_switches(network)
        self._add_routers(network)
        self._add_attackers(network)
        self._add_victims(network)
        self._add_links(network)

        return network

    def _add_switches(self, network: Containernet) -> None:
        """Ajoute tous les switchs à la topologie."""

        for switch in self._config.switches:
            network.addSwitch(switch.name)

    def _add_routers(self, network: Containernet) -> None:
        """Ajoute les routeurs Linux non conteneurisés."""

        for router in self._config.routers:
            network.addHost(router.name, cls=LinuxRouter, ip=None)

    def _add_attackers(self, network: Containernet) -> None:
        """Ajoute les attaquants comme hôtes réseau classiques."""

        for attacker in self._config.attackers:
            network.addHost(
                attacker.name,
                ip=attacker.ip_cidr,
                defaultRoute=f"via {attacker.gateway}",
            )

    def _add_victims(self, network: Containernet) -> None:
        """Ajoute les victimes sous forme de conteneurs Docker."""

        traffic_generator_root = self._config.scripts.normal_traffic.parent

        for victim in self._config.victims:
            network.addDocker(
                victim.name,
                ip=victim.ip_cidr,
                defaultRoute=f"via {victim.gateway}",
                **build_add_docker_options(
                    victim,
                    traffic_generator_root=traffic_generator_root,
                ),
            )

    def _add_links(self, network: Containernet) -> None:
        """Ajoute tous les liens décrits dans la configuration."""

        for link in self._config.links:
            self._add_link(network, link)

    def _add_link(self, network: Containernet, link: LinkSpec) -> None:
        """Convertit un ``LinkSpec`` en appel ``addLink``."""

        options: dict[str, Any] = {}

        if link.left_interface is not None:
            options["intfName1"] = link.left_interface

        if link.right_interface is not None:
            options["intfName2"] = link.right_interface

        if link.left_ip_cidr is not None:
            options["params1"] = {"ip": link.left_ip_cidr}

        if link.right_ip_cidr is not None:
            options["params2"] = {"ip": link.right_ip_cidr}

        if link.bandwidth_mbps is not None:
            options["bw"] = link.bandwidth_mbps

        if link.delay is not None:
            options["delay"] = link.delay

        if link.loss_percent is not None:
            options["loss"] = link.loss_percent

        network.addLink(
            network.get(link.left_node),
            network.get(link.right_node),
            **options,
        )
