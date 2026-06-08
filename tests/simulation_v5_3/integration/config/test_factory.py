"""Tests d'intégration de la factory de configuration V5.3."""

import pytest

from carpet_bombing.simulations.simulation_v5_3.config.factory import (
    build_simulation_config,
)


@pytest.mark.integration
def test_builds_complete_default_configuration() -> None:
    """Vérifie que la factory représente toute la topologie historique."""

    config = build_simulation_config()

    assert len(config.attackers) == 4
    assert len(config.victims) == 20
    assert len(config.routers) == 4
    assert len(config.switches) == 3
    assert len(config.links) == 30
    assert len(config.routes) == 39
    assert all(path.exists() for path in vars(config.scripts).values())


@pytest.mark.integration
def test_applies_runtime_overrides() -> None:
    """Vérifie que les arguments d'exécution remplacent les défauts."""

    config = build_simulation_config(
        scenario_name="carpet",
        duration_seconds=60,
        attack_duration_seconds=40,
        warmup_seconds=10,
        packets_per_second=250,
        protocol="udp",
        fragment_mode="none",
    )

    assert config.scenario.name == "carpet"
    assert config.scenario.duration_seconds == 60
    assert config.scenario.warmup_seconds == 10
    assert config.attack.duration_seconds == 40
    assert config.attack.packets_per_second == 250
    assert config.attack.protocol == "udp"
    assert config.attack.fragment_mode == "none"
