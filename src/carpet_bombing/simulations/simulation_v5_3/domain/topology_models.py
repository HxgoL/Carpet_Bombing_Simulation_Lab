"""Modèles métier décrivant la topologie réseau V5.3.

Ce module ne dépend ni de Mininet ni de Containernet.
"""

from __future__ import annotations

from dataclasses import dataclass


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
    """Décrit une victime active de la simulation."""

    name: str
    ip_cidr: str
    gateway: str
    switch_name: str


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
    """Décrit un lien entre deux nœuds de la topologie.

    Les interfaces et adresses IP sont optionnelles, car les liens entre un
    hôte et un switch ne nécessitent pas toujours une configuration explicite.
    """

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
