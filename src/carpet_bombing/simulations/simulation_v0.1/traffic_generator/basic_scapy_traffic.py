import argparse
import random
import time
from scapy.all import IP, ICMP, TCP, UDP, send

PACKET_COUNT = 50  # Nombre de paquets envoyés par chaque hôte
MIN_DELAY = 0.2  # Délai minimum entre deux paquets
MAX_DELAY = 1.5  # Délai maximum entre deux paquets
TCP_PORTS = [80, 443, 8080]  # Ports TCP utilisés pour le trafic
UDP_PORTS = [53, 123, 5353]  # Ports UDP utilisés pour le trafic

def parse_args():
    # Récupération des arguments passés au script
    # --peers contient la liste des hôtes de destination possibles
    parser = argparse.ArgumentParser()
    parser.add_argument("--peers", required=True)
    return parser.parse_args()


def create_packet(target):
    # Choix aléatoire du protocole à utiliser
    protocol = random.choice(["ICMP", "TCP", "UDP"])

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

    # Transformation de la liste des hôtes en tableau Python
    peers = args.peers.split(",")

    # Envoi de paquets aléatoires vers les autres hôtes
    for _ in range(PACKET_COUNT):
        target = random.choice(peers)
        packet = create_packet(target)

        # Envoi du paquet avec Scapy
        send(packet, verbose=False)

        # Pause aléatoire pour éviter un trafic trop régulier
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    print("Traffic generation completed")


if __name__ == "__main__":
    run()
