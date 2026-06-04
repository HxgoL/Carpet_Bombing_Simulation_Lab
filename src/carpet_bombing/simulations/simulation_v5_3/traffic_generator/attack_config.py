from __future__ import annotations

from dataclasses import dataclass


DEFAULT_TCP_PORTS = [21, 22, 25, 53, 80, 443, 8080]
DEFAULT_UDP_PORTS = [53, 123, 5000, 5353]
AMPLIFICATION_SOURCE_PORTS = [53, 123, 1900, 5353]
ATTACK_PROTOCOLS = ["icmp", "udp", "tcp_syn", "dns_amp"]


@dataclass(frozen=True)
class AttackConfig:
    src_ips: list[str]
    dst_ips: list[str]
    duration: int
    pps: int
    protocol: str
    payload_size: int
    fragment_mode: str
    fragsize: int
    ttl_min: int
    ttl_max: int
    src_rotation_interval: float
    tcp_ports: list[int]
    udp_ports: list[int]
