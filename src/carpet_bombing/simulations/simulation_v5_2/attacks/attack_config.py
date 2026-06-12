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

    def validate(self) -> None:
        if not self.src_ips:
            raise ValueError("At least one source IP is required")
        if not self.dst_ips:
            raise ValueError("At least one destination IP is required")
        if self.duration <= 0:
            raise ValueError("--duration must be greater than zero")
        if self.pps <= 0:
            raise ValueError("--pps must be greater than zero")
        if self.payload_size < 0:
            raise ValueError("--payload-size cannot be negative")
        if self.fragsize <= 0:
            raise ValueError("--fragsize must be greater than zero")
        if not 1 <= self.ttl_min <= self.ttl_max <= 255:
            raise ValueError("TTL values must satisfy 1 <= ttl-min <= ttl-max <= 255")
        if self.src_rotation_interval < 0:
            raise ValueError("--src-rotation-interval cannot be negative")

