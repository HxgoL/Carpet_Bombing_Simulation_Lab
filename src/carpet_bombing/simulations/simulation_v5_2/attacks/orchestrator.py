from pathlib import Path

from carpet_bombing.simulations.simulation_v5_2.config.settings import (
    ATTACK_TARGET_RANGE,
    DEFAULT_FRAGSIZE,
    DEFAULT_PAYLOAD_SIZE,
    DEFAULT_SRC_ROTATION_INTERVAL,
    DEFAULT_TTL_MAX,
    DEFAULT_TTL_MIN,
    SOURCE_RANGES,
    SINGLE_TARGET_IP,
)


ATTACK_SCRIPT = Path(__file__).resolve().parents[1] / "attacks" / "fragmented_carpet_bombing.py"


def launch_attack(
    attackers,
    scenario_name,
    destination_args,
    attack_duration,
    pps,
    protocol,
    fragment_mode,
):
    for attacker, source_range, destination_arg in zip(attackers, SOURCE_RANGES, destination_args):
        attacker.cmd(
            f"timeout {attack_duration} python3 {ATTACK_SCRIPT} "
            f"{destination_arg} "
            f"--src-range {source_range} "
            f"--duration {attack_duration} "
            f"--pps {pps} "
            f"--protocol {protocol} "
            f"--fragment-mode {fragment_mode} "
            f"--fragsize {DEFAULT_FRAGSIZE} "
            f"--payload-size {DEFAULT_PAYLOAD_SIZE} "
            f"--ttl-min {DEFAULT_TTL_MIN} "
            f"--ttl-max {DEFAULT_TTL_MAX} "
            f"--src-rotation-interval {DEFAULT_SRC_ROTATION_INTERVAL} "
            f"> /tmp/{attacker.name}_{scenario_name}_attack_v5_2.log 2>&1 &"
        )


def launch_single_target_attack(
    attackers,
    attack_duration,
    pps,
    protocol,
    fragment_mode,
):
    launch_attack(
        attackers=attackers,
        scenario_name="single_target",
        destination_args=[f"--dst-ip {SINGLE_TARGET_IP}"] * len(attackers),
        attack_duration=attack_duration,
        pps=pps,
        protocol=protocol,
        fragment_mode=fragment_mode,
    )


def launch_fragmented_carpet_attack(
    attackers,
    attack_duration,
    pps,
    protocol,
    fragment_mode,
):
    launch_attack(
        attackers=attackers,
        scenario_name="carpet",
        destination_args=[f"--dst-range {ATTACK_TARGET_RANGE}"] * len(attackers),
        attack_duration=attack_duration,
        pps=pps,
        protocol=protocol,
        fragment_mode=fragment_mode,
    )


def stop_fragmented_carpet_attack(attackers):
    for attacker in attackers:
        attacker.cmd("pkill -f fragmented_carpet_bombing.py")
