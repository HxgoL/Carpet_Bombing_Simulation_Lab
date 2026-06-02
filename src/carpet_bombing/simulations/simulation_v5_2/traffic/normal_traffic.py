import argparse
import random
import time

from scapy.all import ICMP, IP, TCP, UDP, send


MIN_DELAY = 4.0
MAX_DELAY = 10.0
TCP_PORTS = [80, 443, 8080]
UDP_PORTS = [53, 123, 5353]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--peers", required=True)
    parser.add_argument("--min-delay", type=float, default=MIN_DELAY)
    parser.add_argument("--max-delay", type=float, default=MAX_DELAY)
    return parser.parse_args()


def create_packet(target):
    protocol = random.choice(["ICMP", "TCP", "UDP", "UDP"])

    if protocol == "ICMP":
        return IP(dst=target) / ICMP()

    if protocol == "TCP":
        return IP(dst=target) / TCP(dport=random.choice(TCP_PORTS), flags="S")

    return IP(dst=target) / UDP(dport=random.choice(UDP_PORTS))


def run():
    args = parse_args()
    peers = args.peers.split(",")

    while True:
        send(create_packet(random.choice(peers)), verbose=False)
        time.sleep(random.uniform(args.min_delay, args.max_delay))


if __name__ == "__main__":
    run()
