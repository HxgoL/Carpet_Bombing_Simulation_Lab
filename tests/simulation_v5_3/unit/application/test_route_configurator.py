"""Tests unitaires du service de configuration des routes."""

import pytest

from carpet_bombing.simulations.simulation_v5_3.application.route_configurator import (
    RouteConfigurator,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    RouteSpec,
)
from tests.simulation_v5_3.fakes.runners import CommandCall, FakeCommandRunner


@pytest.mark.unit
def test_configures_each_route_with_linux_ip_command() -> None:
    """Vérifie la traduction des routes en commandes Linux."""

    runner = FakeCommandRunner()
    configurator = RouteConfigurator(runner)

    configurator.configure(
        (
            RouteSpec("r1", "10.0.0.0/24", "10.10.1.2"),
            RouteSpec("a1", "default", "10.0.1.254"),
        )
    )

    assert runner.calls == [
        CommandCall(
            "r1",
            ("ip", "route", "replace", "10.0.0.0/24", "via", "10.10.1.2"),
        ),
        CommandCall(
            "a1",
            ("ip", "route", "replace", "default", "via", "10.0.1.254"),
        ),
    ]
