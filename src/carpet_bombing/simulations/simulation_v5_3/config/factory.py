"""Factory construisant une configuration V5.3 complète et validée."""

from pathlib import Path

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


SIMULATION_ROOT = Path(__file__).resolve().parents[1]
TRAFFIC_GENERATOR_ROOT = SIMULATION_ROOT / "traffic_generator"


def build_simulation_config(
    *,
    scenario_name: ScenarioName | None = None,
    duration_seconds: int = DEFAULT_SCENARIO_DURATION_SECONDS,
    attack_duration_seconds: int = DEFAULT_ATTACK_DURATION_SECONDS,
    warmup_seconds: int = DEFAULT_WARMUP_SECONDS,
    packets_per_second: int = DEFAULT_PACKETS_PER_SECOND,
    protocol: AttackProtocol = DEFAULT_ATTACK_PROTOCOL,
    fragment_mode: FragmentMode = DEFAULT_FRAGMENT_MODE,
) -> SimulationConfig:
    """Construit la configuration par défaut avec les options d'exécution."""

    attackers = tuple(
        AttackerSpec(**definition)
        for definition in ATTACKER_DEFINITIONS
    )
    victims = tuple(
        VictimSpec(
            name=f"h{index}",
            ip_cidr=f"{ip_address}/24",
            gateway=VICTIM_GATEWAY,
            switch_name=VICTIM_SWITCH_NAME,
        )
        for index, ip_address in enumerate(ACTIVE_VICTIM_IPS, start=1)
    )

    links = (
        *(LinkSpec(**definition) for definition in CORE_LINK_DEFINITIONS),
        *(LinkSpec(attacker.name, attacker.switch_name) for attacker in attackers),
        *(LinkSpec(victim.name, victim.switch_name) for victim in victims),
    )

    routes = (
        *(RouteSpec(**definition) for definition in ROUTE_DEFINITIONS),
        *(RouteSpec(attacker.name, "default", attacker.gateway) for attacker in attackers),
        *(RouteSpec(victim.name, "default", victim.gateway) for victim in victims),
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
