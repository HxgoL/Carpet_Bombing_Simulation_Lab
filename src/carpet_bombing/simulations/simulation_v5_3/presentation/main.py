"""Point d'entrée principal de la simulation V5.3."""

from __future__ import annotations

import argparse
from typing import cast

from mininet.log import setLogLevel

from carpet_bombing.simulations.simulation_v5_3.application.attack_service import (
    AttackService,
)
from carpet_bombing.simulations.simulation_v5_3.application.route_configurator import (
    RouteConfigurator,
)
from carpet_bombing.simulations.simulation_v5_3.application.scenario_runner import (
    ScenarioRunner,
)
from carpet_bombing.simulations.simulation_v5_3.application.simulation_service import (
    SimulationService,
)
from carpet_bombing.simulations.simulation_v5_3.application.traffic_service import (
    TrafficService,
)
from carpet_bombing.simulations.simulation_v5_3.config.factory import (
    build_simulation_config,
)
from carpet_bombing.simulations.simulation_v5_3.domain.attack_models import (
    AttackProtocol,
    FragmentMode,
)
from carpet_bombing.simulations.simulation_v5_3.domain.scenario_models import (
    ScenarioName,
)
from carpet_bombing.simulations.simulation_v5_3.infrastructure.mininet.process_runner import (
    MininetCommandRunner,
    MininetProcessRunner,
)
from carpet_bombing.simulations.simulation_v5_3.infrastructure.mininet.topology_builder import (
    MininetTopologyBuilder,
)
from carpet_bombing.simulations.simulation_v5_3.infrastructure.system_clock import (
    SystemClock,
)
from carpet_bombing.simulations.simulation_v5_3.presentation.cli_commands import (
    MininetInteractiveCli,
)


def parse_args() -> argparse.Namespace:
    """Analyse les arguments fournis par l'utilisateur."""

    parser = argparse.ArgumentParser(
        description="Run the V5.3 Mininet topology."
    )

    parser.add_argument(
        "--auto-scenario",
        choices=["normal", "single_target", "carpet"],
    )
    parser.add_argument("--duration", type=int, default=45)
    parser.add_argument("--attack-duration", type=int, default=30)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--pps", type=int, default=120)
    parser.add_argument(
        "--protocol",
        choices=["icmp", "udp", "tcp_syn", "dns_amp", "mixed"],
        default="mixed",
    )
    parser.add_argument(
        "--fragment-mode",
        choices=["manual", "auto", "none"],
        default="manual",
    )

    return parser.parse_args()


def main() -> None:
    """Construit les dépendances puis lance la simulation."""

    args = parse_args()
    setLogLevel("info")

    config = build_simulation_config(
        scenario_name=cast(ScenarioName | None, args.auto_scenario),
        duration_seconds=args.duration,
        attack_duration_seconds=args.attack_duration,
        warmup_seconds=args.warmup,
        packets_per_second=args.pps,
        protocol=cast(AttackProtocol, args.protocol),
        fragment_mode=cast(FragmentMode, args.fragment_mode),
    )

    network = MininetTopologyBuilder(config).build()

    command_runner = MininetCommandRunner(network)
    process_runner = MininetProcessRunner(network)
    clock = SystemClock()

    route_configurator = RouteConfigurator(command_runner)
    traffic_service = TrafficService(config, process_runner)
    attack_service = AttackService(config, process_runner)
    scenario_runner = ScenarioRunner(config, attack_service, clock)
    interactive_cli = MininetInteractiveCli(network, attack_service)

    simulation_service = SimulationService(
        config=config,
        network=network,
        route_configurator=route_configurator,
        traffic_service=traffic_service,
        attack_service=attack_service,
        scenario_runner=scenario_runner,
        interactive_cli=interactive_cli,
    )

    try:
        simulation_service.run()
    finally:
        # close() est idempotente : cet appel reste sûr même si run() l'a appelée.
        simulation_service.close()


if __name__ == "__main__":
    main()
