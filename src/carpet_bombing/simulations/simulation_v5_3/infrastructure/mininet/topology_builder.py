"""Builder responsable de la construction de la topologie Mininet."""

from __future__ import annotations

from typing import Any

from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import OVSBridge

from carpet_bombing.simulations.simulation_v5_3.domain.simulation_models import (
    SimulationConfig,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import LinkSpec
from carpet_bombing.simulations.simulation_v5_3.infrastructure.mininet.linux_router import (
    LinuxRouter,
)


class MininetTopologyBuilder:
    """Construit un réseau Mininet depuis une configuration de simulation."""

    def __init__(self, config: SimulationConfig) -> None:
        """Conserve la configuration à transformer en topologie Mininet."""
        self._config = config

    def build(self) -> Mininet:
        """Construit et retourne un réseau Mininet non démarré."""
        network = Mininet(controller=None, switch=OVSBridge, link=TCLink)

        self._add_switches(network)
        self._add_routers(network)
        self._add_attackers(network)
        self._add_victims(network)
        self._add_links(network)

        return network

    def _add_switches(self, network: Mininet) -> None:
        """Ajoute tous les switchs à la topologie."""

        for switch in self._config.switches:
            network.addSwitch(switch.name)

    def _add_routers(self, network: Mininet) -> None:
        """Ajoute les routeurs Linux à la topologie."""

        for router in self._config.routers:
            # Les adresses des interfaces sont portées par les LinkSpec.
            # ``ip=None`` évite que Mininet écrase l'IP de l'interface par défaut.
            network.addHost(router.name, cls=LinuxRouter, ip=None)

    def _add_attackers(self, network: Mininet) -> None:
        """Ajoute les attaquants avec leur route par défaut."""

        for attacker in self._config.attackers:
            network.addHost(
                attacker.name,
                ip=attacker.ip_cidr,
                defaultRoute=f"via {attacker.gateway}",
            )

    def _add_victims(self, network: Mininet) -> None:
        """Ajoute les victimes actives avec leur route par défaut."""

        for victim in self._config.victims:
            network.addHost(
                victim.name,
                ip=victim.ip_cidr,
                defaultRoute=f"via {victim.gateway}",
            )

    def _add_links(self, network: Mininet) -> None:
        """Ajoute tous les liens décrits dans la configuration."""

        for link in self._config.links:
            self._add_link(network, link)

    def _add_link(self, network: Mininet, link: LinkSpec) -> None:
        """Convertit un LinkSpec en appel Mininet addLink()."""

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

        left_node = network.get(link.left_node)
        right_node = network.get(link.right_node)

        network.addLink(left_node, right_node, **options)
