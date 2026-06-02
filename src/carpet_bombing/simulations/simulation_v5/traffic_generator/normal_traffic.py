import argparse
import random
import time
from scapy.all import ICMP, IP, TCP, UDP, send

MIN_DELAY = 5.0  # Délai minimum entre deux paquets
MAX_DELAY = 12.0  # Délai maximum entre deux paquets
TCP_PORTS = [80, 443, 8080]  # Ports TCP utilisés pour le trafic
UDP_PORTS = [53, 123, 5353]  # Ports UDP utilisés pour le trafic

def parse_args():
    # Récupération des arguments passés au script
    # --peers contient la liste des victimes de destination possibles
    parser = argparse.ArgumentParser()
    parser.add_argument("--peers", required=True)
    parser.add_argument("--min-delay", type=float, default=MIN_DELAY)
    parser.add_argument("--max-delay", type=float, default=MAX_DELAY)
    return parser.parse_args()

def create_packet(target):
    # Choix aléatoire du protocole à utiliser
    protocol = random.choice(["ICMP", "TCP", "UDP", "UDP"])

    # Création d'un paquet ICMP vers la cible
    if protocol == "ICMP":
        return IP(dst=target) / ICMP()

    # Création d'un paquet TCP SYN vers un port aléatoire
    if protocol == "TCP":
        return IP(dst=target) / TCP(dport=random.choice(TCP_PORTS), flags="S")

    # Création d'un paquet UDP vers un port aléatoire
    return IP(dst=target) / UDP(dport=random.choice(UDP_PORTS))

def run():
    # Récupération des arguments du script
    args = parse_args()

    # Transformation de la liste des victimes en tableau Python
    peers = args.peers.split(",")

    # Envoi continu de paquets aléatoires vers les autres victimes
    while True:
        target = random.choice(peers)
        packet = create_packet(target)

        # Envoi du paquet avec Scapy
        send(packet, verbose=False)

        # Pause aléatoire pour éviter un trafic trop régulier
        time.sleep(random.uniform(args.min_delay, args.max_delay))

if __name__ == "__main__":
    run()
