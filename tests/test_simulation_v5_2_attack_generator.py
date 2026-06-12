import sys
from pathlib import Path

import pytest
from scapy.all import ICMP, IP, TCP, UDP


ATTACKS_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "carpet_bombing"
    / "simulations"
    / "simulation_v5_2"
    / "attacks"
)
sys.path.insert(0, str(ATTACKS_DIR))

from attack_config import AttackConfig  # noqa: E402
from ip_parsing import parse_ip_range  # noqa: E402
from packet_factory import build_packet  # noqa: E402


def make_config(protocol: str) -> AttackConfig:
    return AttackConfig(
        src_ips=["10.10.1.1"],
        dst_ips=["10.20.0.10"],
        duration=1,
        pps=1,
        protocol=protocol,
        payload_size=20,
        fragment_mode="none",
        fragsize=300,
        ttl_min=42,
        ttl_max=42,
        src_rotation_interval=5.0,
        tcp_ports=[443],
        udp_ports=[53],
    )


@pytest.mark.parametrize(
    ("protocol", "layer"),
    [("icmp", ICMP), ("udp", UDP), ("tcp_syn", TCP), ("dns_amp", UDP)],
)
def test_packet_factory_builds_supported_protocols(protocol, layer):
    packet = build_packet("10.10.1.1", "10.20.0.10", protocol, make_config(protocol))

    assert packet.haslayer(IP)
    assert packet.haslayer(layer)
    assert packet[IP].ttl == 42


def test_parse_ip_range_is_inclusive():
    assert parse_ip_range("10.0.0.1-10.0.0.3") == [
        "10.0.0.1",
        "10.0.0.2",
        "10.0.0.3",
    ]


def test_config_rejects_invalid_ttl_range():
    config = make_config("udp")
    invalid_config = AttackConfig(**{**config.__dict__, "ttl_min": 65, "ttl_max": 64})

    with pytest.raises(ValueError, match="TTL"):
        invalid_config.validate()
