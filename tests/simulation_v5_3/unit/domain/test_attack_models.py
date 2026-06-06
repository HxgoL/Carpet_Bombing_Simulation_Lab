"""Tests unitaires des paramètres d'attaque."""

from dataclasses import replace

import pytest

from carpet_bombing.simulations.simulation_v5_3.domain.attack_models import (
    AttackSettings,
)

#prep les données de test
@pytest.fixture
def valid_attack_settings() -> AttackSettings:
    """Retourne une configuration d'attaque valide."""

    return AttackSettings(
        duration_seconds=30,
        packets_per_second=120,
        protocol="mixed",
        fragment_mode="manual",
    )

#bloc de test avec parametrize pour en lancer plusieurs
@pytest.mark.unit
@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("duration_seconds", -1),
        ("packets_per_second", 0),
        ("payload_size", 0),
        ("fragment_size", 0),
    ],
)
def test_rejects_invalid_numeric_settings(
    valid_attack_settings: AttackSettings,
    field_name: str,
    invalid_value: int,
) -> None:
    """Vérifie que les paramètres numériques invalides sont refusés."""

    with pytest.raises(ValueError):
        replace(valid_attack_settings, **{field_name: invalid_value})

@pytest.mark.unit
def test_rejects_inverted_ttl_range(
    valid_attack_settings: AttackSettings,
) -> None:
    """Vérifie que le TTL minimal ne dépasse pas le TTL maximal."""

    with pytest.raises(ValueError):
        replace(valid_attack_settings, ttl_min=65, ttl_max=64)
