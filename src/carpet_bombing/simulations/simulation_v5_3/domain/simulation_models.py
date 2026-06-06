"""Modèles regroupant la configuration complète d'une simulation."""

from dataclasses import dataclass
from pathlib import Path

from .attack_models import AttackSettings
from .scenario_models import ScenarioSettings
from .topology_models import (
    AttackerSpec,
    LinkSpec,
    RouteSpec,
    RouterSpec,
    SwitchSpec,
    VictimSpec,
)


@dataclass(frozen=True)
class ScriptPaths:
    """Regroupe les chemins des scripts exécutés dans les hôtes."""

    normal_traffic: Path
    packet_receiver: Path
    attack_generator: Path


@dataclass(frozen=True)
class SimulationConfig:
    """Décrit intégralement une simulation V5.3."""

    attackers: tuple[AttackerSpec, ...]
    victims: tuple[VictimSpec, ...]
    routers: tuple[RouterSpec, ...]
    switches: tuple[SwitchSpec, ...]
    links: tuple[LinkSpec, ...]
    routes: tuple[RouteSpec, ...]

    attack: AttackSettings
    scenario: ScenarioSettings
    scripts: ScriptPaths

    single_target_ip: str
    victim_gateway: str

    def __post_init__(self) -> None:
        """Détecte les incohérences simples dans la configuration."""

        if not self.attackers:
            raise ValueError("The simulation must contain at least one attacker.")

        if not self.victims:
            raise ValueError("The simulation must contain at least one victim.")

        node_names = {
            *(attacker.name for attacker in self.attackers),
            *(victim.name for victim in self.victims),
            *(router.name for router in self.routers),
            *(switch.name for switch in self.switches),
        }

        node_count = (
            len(self.attackers)
            + len(self.victims)
            + len(self.routers)
            + len(self.switches)
        )

        if len(node_names) != node_count:
            raise ValueError("Every topology node must have a unique name.")

        for link in self.links:
            if link.left_node not in node_names or link.right_node not in node_names:
                raise ValueError(f"Link references an unknown node: {link}")

        for route in self.routes:
            if route.node_name not in node_names:
                raise ValueError(f"Route references an unknown node: {route}")