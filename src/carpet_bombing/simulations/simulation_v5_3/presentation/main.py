"""Point d'entrée principal de la simulation V5.3."""

from __future__ import annotations

import argparse
from typing import cast

from mininet.log import setLogLevel

from carpet_bombing.simulations.simulation_v5_3.application.attack_service import (
    AttackService,
)
from carpet_bombing.simulations.simulation_v5_3.application.ports import (
    CommandRunner,
    ProcessRunner,
    SimulationNetwork,
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
    BackendName,
    build_simulation_config,
)
from carpet_bombing.simulations.simulation_v5_3.config.service_defaults import (
    FASTAPI_IMAGE,
)
from carpet_bombing.simulations.simulation_v5_3.domain.attack_models import (
    AttackProtocol,
    FragmentMode,
)
from carpet_bombing.simulations.simulation_v5_3.domain.scenario_models import (
    ScenarioName,
)
from carpet_bombing.simulations.simulation_v5_3.domain.simulation_models import (
    SimulationConfig,
)
from carpet_bombing.simulations.simulation_v5_3.infrastructure.docker.docker_paths import (
    FASTAPI_DOCKER_CONTEXT,
)
from carpet_bombing.simulations.simulation_v5_3.infrastructure.docker.image_builder import (
    ensure_image,
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
        description="Run the V5.3 Mininet or Containernet topology."
    )

    parser.add_argument(
        "--backend",
        choices=["mininet", "containernet"],
        default="mininet",
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
    backend = cast(BackendName, args.backend)

    config = build_simulation_config(
        backend=backend,
        scenario_name=cast(ScenarioName | None, args.auto_scenario),
        duration_seconds=args.duration,
        attack_duration_seconds=args.attack_duration,
        warmup_seconds=args.warmup,
        packets_per_second=args.pps,
        protocol=cast(AttackProtocol, args.protocol),
        fragment_mode=cast(FragmentMode, args.fragment_mode),
    )

    network, command_runner, process_runner = _build_backend(
        backend,
        config,
    )
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

def _build_backend(
    backend: BackendName,
    config: SimulationConfig,
) -> tuple[SimulationNetwork, CommandRunner, ProcessRunner]:
    """Construit les adaptateurs correspondant au backend sélectionné."""

    if backend == "containernet":
        # Les imports sont retardés afin que le backend Mininet reste utilisable
        # sur une machine où Containernet n'est pas installé.
        from carpet_bombing.simulations.simulation_v5_3.infrastructure.containernet.process_runner import (
            ContainernetCommandRunner,
            ContainernetProcessRunner,
        )
        from carpet_bombing.simulations.simulation_v5_3.infrastructure.containernet.topology_builder import (
            ContainernetTopologyBuilder,
        )

        ensure_image(FASTAPI_IMAGE, FASTAPI_DOCKER_CONTEXT)
        network = ContainernetTopologyBuilder(config).build()

        return (
            network,
            ContainernetCommandRunner(network),
            ContainernetProcessRunner(network),
        )

    from carpet_bombing.simulations.simulation_v5_3.infrastructure.mininet.process_runner import (
        MininetCommandRunner,
        MininetProcessRunner,
    )
    from carpet_bombing.simulations.simulation_v5_3.infrastructure.mininet.topology_builder import (
        MininetTopologyBuilder,
    )

    network = MininetTopologyBuilder(config).build()

    return (
        network,
        MininetCommandRunner(network),
        MininetProcessRunner(network),
    )


if __name__ == "__main__":
    main()
