"""Tests unitaires de la configuration complète."""

from dataclasses import replace
from pathlib import Path

import pytest

from carpet_bombing.simulations.simulation_v5_3.domain.attack_models import (
    AttackSettings,
)
from carpet_bombing.simulations.simulation_v5_3.domain.scenario_models import (
    ScenarioSettings,
)
from carpet_bombing.simulations.simulation_v5_3.domain.simulation_models import (
    ScriptPaths,
    SimulationConfig,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    AttackerSpec,
    LinkSpec,
    RouterSpec,
    SwitchSpec,
    VictimSpec,
)


def build_valid_config() -> SimulationConfig:
    """Construit une configuration minimale valide pour les tests."""

    return SimulationConfig(
        attackers=(
            AttackerSpec(
                name="a1",
                ip_cidr="10.0.1.1/24",
                gateway="10.0.1.254",
                switch_name="s1",
                simulated_source_range="192.0.2.1-192.0.2.10",
                carpet_target_range="10.0.0.1-10.0.0.10",
            ),
        ),
        victims=(
            VictimSpec("h1", "10.0.0.1/24", "10.0.0.254", "s2"),
        ),
        routers=(RouterSpec("r1"),),
        switches=(SwitchSpec("s1"), SwitchSpec("s2")),
        links=(LinkSpec("a1", "s1"), LinkSpec("h1", "s2")),
        routes=(),
        attack=AttackSettings(30, 120, "mixed", "manual"),
        scenario=ScenarioSettings("carpet", 45, 5),
        scripts=ScriptPaths(Path("normal.py"), Path("receiver.py"), Path("attack.py")),
        single_target_ip="10.0.0.1",
        victim_gateway="10.0.0.254",
    )


@pytest.mark.unit
def test_accepts_valid_simulation_config() -> None:
    """Vérifie qu'une configuration complète cohérente est acceptée."""

    config = build_valid_config()

    assert len(config.attackers) == 1
    assert len(config.victims) == 1


@pytest.mark.unit
def test_rejects_missing_attackers() -> None:
    """Vérifie qu'une simulation doit contenir un attaquant."""

    with pytest.raises(ValueError):
        replace(build_valid_config(), attackers=())


@pytest.mark.unit
def test_rejects_unknown_link_node() -> None:
    """Vérifie qu'un lien ne référence pas un nœud inconnu."""

    with pytest.raises(ValueError):
        replace(build_valid_config(), links=(LinkSpec("a1", "unknown"),))
