import argparse
import random
import time

from scapy.all import ICMP, IP, TCP, UDP, send


MIN_DELAY = 5.0
MAX_DELAY = 12.0
TCP_PORTS = [80, 443, 8080]
UDP_PORTS = [53, 123, 5353]
PROTOCOL_WEIGHTS = ["ICMP", "TCP", "UDP", "UDP"]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate lightweight normal victim traffic.")
    parser.add_argument("--peers", required=True)
    parser.add_argument("--min-delay", type=float, default=MIN_DELAY)
    parser.add_argument("--max-delay", type=float, default=MAX_DELAY)
    return parser.parse_args()


def build_icmp_packet(target):
    return IP(dst=target) / ICMP()


def build_tcp_packet(target):
    return IP(dst=target) / TCP(dport=random.choice(TCP_PORTS), flags="S")


def build_udp_packet(target):
    return IP(dst=target) / UDP(dport=random.choice(UDP_PORTS))


def create_packet(target):
    protocol = random.choice(PROTOCOL_WEIGHTS)

    if protocol == "ICMP":
        return build_icmp_packet(target)

    if protocol == "TCP":
        return build_tcp_packet(target)

    return build_udp_packet(target)


def run():
    args = parse_args()
    peers = [peer for peer in args.peers.split(",") if peer]

    while True:
        send(create_packet(random.choice(peers)), verbose=False)
        time.sleep(random.uniform(args.min_delay, args.max_delay))


if __name__ == "__main__":
    run()
