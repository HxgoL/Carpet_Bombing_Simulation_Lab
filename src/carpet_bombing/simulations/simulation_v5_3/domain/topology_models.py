"""Modèles métier décrivant la topologie réseau V5.3.

Ce module ne dépend ni de Mininet, ni de Containernet, ni de Docker.
"""

from __future__ import annotations

from dataclasses import dataclass

from .service_models import ContainerSpec, ServiceSpec


@dataclass(frozen=True)
class AttackerSpec:
    """Décrit un attaquant et les plages qu'il utilise."""

    name: str
    ip_cidr: str
    gateway: str
    switch_name: str
    simulated_source_range: str
    carpet_target_range: str


@dataclass(frozen=True)
class VictimSpec:
    """Décrit une victime classique ou conteneurisée."""

    name: str
    ip_cidr: str
    gateway: str
    switch_name: str

    container: ContainerSpec | None = None
    service: ServiceSpec | None = None

    def __post_init__(self) -> None:
        """Vérifie qu'un service possède un environnement d'exécution."""

        if self.service is not None and self.container is None:
            raise ValueError(
                "A victim service requires a container specification."
            )

    @property
    def is_containerized(self) -> bool:
        """Indique si la victime doit être créée dans un conteneur."""

        return self.container is not None


@dataclass(frozen=True)
class RouterSpec:
    """Décrit un routeur Linux utilisé dans la topologie."""

    name: str


@dataclass(frozen=True)
class SwitchSpec:
    """Décrit un switch virtuel de la topologie."""

    name: str


@dataclass(frozen=True)
class LinkSpec:
    """Décrit un lien entre deux nœuds de la topologie."""

    left_node: str
    right_node: str

    left_interface: str | None = None
    right_interface: str | None = None

    left_ip_cidr: str | None = None
    right_ip_cidr: str | None = None

    bandwidth_mbps: int | None = None
    delay: str | None = None
    loss_percent: float | None = None


@dataclass(frozen=True)
class RouteSpec:
    """Décrit une route statique à installer sur un nœud."""

    node_name: str
    destination: str
    gateway: str