"""Tests unitaires du configurateur d'interfaces réseau."""

import pytest

from carpet_bombing.simulations.simulation_v5_3.application.interface_configurator import (
    InterfaceConfigurator,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    LinkSpec,
)
from tests.simulation_v5_3.fakes.runners import CommandCall, FakeCommandRunner


@pytest.mark.unit
def test_configures_only_link_endpoints_with_interface_addresses() -> None:
    """Vérifie que les adresses déclarées sont appliquées aux bonnes interfaces."""

    runner = FakeCommandRunner()
    configurator = InterfaceConfigurator(runner)

    configurator.configure(
        (
            LinkSpec(
                left_node="r1",
                right_node="r_core",
                left_interface="r1-eth1",
                right_interface="r_core-eth0",
                left_ip_cidr="10.10.1.1/30",
                right_ip_cidr="10.10.1.2/30",
            ),
            LinkSpec(left_node="a1", right_node="s1"),
        )
    )

    assert runner.calls == [
        CommandCall(
            "r1",
            ("ip", "link", "set", "dev", "r1-eth1", "up"),
        ),
        CommandCall(
            "r1",
            ("ip", "address", "replace", "10.10.1.1/30", "dev", "r1-eth1"),
        ),
        CommandCall(
            "r_core",
            ("ip", "link", "set", "dev", "r_core-eth0", "up"),
        ),
        CommandCall(
            "r_core",
            (
                "ip",
                "address",
                "replace",
                "10.10.1.2/30",
                "dev",
                "r_core-eth0",
            ),
        ),
    ]
