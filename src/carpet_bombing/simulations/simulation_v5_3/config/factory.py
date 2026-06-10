"""Factory construisant une configuration V5.3 complète et validée."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from carpet_bombing.simulations.simulation_v5_3.config.defaults import (
    DEFAULT_ATTACK_DURATION_SECONDS,
    DEFAULT_ATTACK_PROTOCOL,
    DEFAULT_FRAGMENT_MODE,
    DEFAULT_FRAGMENT_SIZE,
    DEFAULT_PACKETS_PER_SECOND,
    DEFAULT_PAYLOAD_SIZE,
    DEFAULT_SCENARIO_DURATION_SECONDS,
    DEFAULT_SOURCE_ROTATION_INTERVAL_SECONDS,
    DEFAULT_TTL_MAX,
    DEFAULT_TTL_MIN,
    DEFAULT_WARMUP_SECONDS,
    SINGLE_TARGET_IP,
    VICTIM_GATEWAY,
    VICTIM_SWITCH_NAME,
)
from carpet_bombing.simulations.simulation_v5_3.config.service_defaults import (
    FASTAPI_ENVIRONMENT,
    FASTAPI_HEALTHCHECK_PATH,
    FASTAPI_IMAGE,
    FASTAPI_INTERNAL_PORT,
    FASTAPI_SERVICE_NAME,
    FASTAPI_START_COMMAND,
)
from carpet_bombing.simulations.simulation_v5_3.config.topology_defaults import (
    ACTIVE_VICTIM_IPS,
    ATTACKER_DEFINITIONS,
    CORE_LINK_DEFINITIONS,
    ROUTE_DEFINITIONS,
    ROUTER_NAMES,
    SWITCH_NAMES,
)
from carpet_bombing.simulations.simulation_v5_3.domain.attack_models import (
    AttackProtocol,
    AttackSettings,
    FragmentMode,
)
from carpet_bombing.simulations.simulation_v5_3.domain.scenario_models import (
    ScenarioName,
    ScenarioSettings,
)
from carpet_bombing.simulations.simulation_v5_3.domain.service_models import (
    ContainerSpec,
    ServiceSpec,
)
from carpet_bombing.simulations.simulation_v5_3.domain.simulation_models import (
    ScriptPaths,
    SimulationConfig,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    AttackerSpec,
    LinkSpec,
    RouteSpec,
    RouterSpec,
    SwitchSpec,
    VictimSpec,
)


BackendName = Literal["mininet", "containernet"]

SIMULATION_ROOT = Path(__file__).resolve().parents[1]
TRAFFIC_GENERATOR_ROOT = SIMULATION_ROOT / "traffic_generator"


def build_simulation_config(
    *,
    backend: BackendName = "mininet",
    scenario_name: ScenarioName | None = None,
    duration_seconds: int = DEFAULT_SCENARIO_DURATION_SECONDS,
    attack_duration_seconds: int = DEFAULT_ATTACK_DURATION_SECONDS,
    warmup_seconds: int = DEFAULT_WARMUP_SECONDS,
    packets_per_second: int = DEFAULT_PACKETS_PER_SECOND,
    protocol: AttackProtocol = DEFAULT_ATTACK_PROTOCOL,
    fragment_mode: FragmentMode = DEFAULT_FRAGMENT_MODE,
) -> SimulationConfig:
    """Construit une configuration adaptée au backend demandé."""

    if backend not in ("mininet", "containernet"):
        raise ValueError(f"Unsupported simulation backend: {backend}")

    attackers = _build_attackers()
    victims = _build_victims(backend)

    links = (
        *(LinkSpec(**definition) for definition in CORE_LINK_DEFINITIONS),
        *(
            LinkSpec(attacker.name, attacker.switch_name)
            for attacker in attackers
        ),
        *(
            LinkSpec(
                victim.name,
                victim.switch_name,
                left_interface=f"{victim.name}-eth0",
                left_ip_cidr=victim.ip_cidr,
            )
            for victim in victims
        ),
    )

    routes = (
        *(RouteSpec(**definition) for definition in ROUTE_DEFINITIONS),
        *(
            RouteSpec(attacker.name, "default", attacker.gateway)
            for attacker in attackers
        ),
        *(
            RouteSpec(victim.name, "default", victim.gateway)
            for victim in victims
        ),
    )

    return SimulationConfig(
        attackers=attackers,
        victims=victims,
        routers=tuple(RouterSpec(name) for name in ROUTER_NAMES),
        switches=tuple(SwitchSpec(name) for name in SWITCH_NAMES),
        links=links,
        routes=routes,
        attack=AttackSettings(
            duration_seconds=attack_duration_seconds,
            packets_per_second=packets_per_second,
            protocol=protocol,
            fragment_mode=fragment_mode,
            payload_size=DEFAULT_PAYLOAD_SIZE,
            fragment_size=DEFAULT_FRAGMENT_SIZE,
            ttl_min=DEFAULT_TTL_MIN,
            ttl_max=DEFAULT_TTL_MAX,
            source_rotation_interval_seconds=(
                DEFAULT_SOURCE_ROTATION_INTERVAL_SECONDS
            ),
        ),
        scenario=ScenarioSettings(
            name=scenario_name,
            duration_seconds=duration_seconds,
            warmup_seconds=warmup_seconds,
        ),
        scripts=ScriptPaths(
            normal_traffic=TRAFFIC_GENERATOR_ROOT / "normal_traffic.py",
            packet_receiver=TRAFFIC_GENERATOR_ROOT / "packet_receiver.py",
            attack_generator=(
                TRAFFIC_GENERATOR_ROOT / "advanced_carpet_bombing_attack.py"
            ),
        ),
        single_target_ip=SINGLE_TARGET_IP,
        victim_gateway=VICTIM_GATEWAY,
    )


def _build_attackers() -> tuple[AttackerSpec, ...]:
    """Construit les attaquants de la topologie."""

    return tuple(
        AttackerSpec(**definition)
        for definition in ATTACKER_DEFINITIONS
    )


def _build_victims(backend: BackendName) -> tuple[VictimSpec, ...]:
    """Construit des victimes classiques ou conteneurisées."""

    container: ContainerSpec | None = None
    service: ServiceSpec | None = None

    if backend == "containernet":
        container = ContainerSpec(
            image=FASTAPI_IMAGE,
            environment=FASTAPI_ENVIRONMENT,
        )
        service = ServiceSpec(
            name=FASTAPI_SERVICE_NAME,
            internal_port=FASTAPI_INTERNAL_PORT,
            start_command=FASTAPI_START_COMMAND,
            healthcheck_path=FASTAPI_HEALTHCHECK_PATH,
        )

    return tuple(
        VictimSpec(
            name=f"h{index}",
            ip_cidr=f"{ip_address}/24",
            gateway=VICTIM_GATEWAY,
            switch_name=VICTIM_SWITCH_NAME,
            container=container,
            service=service,
        )
        for index, ip_address in enumerate(ACTIVE_VICTIM_IPS, start=1)
    )
