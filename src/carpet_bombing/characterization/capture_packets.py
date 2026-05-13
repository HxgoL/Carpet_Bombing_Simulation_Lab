import argparse
import shlex
import signal
import subprocess
import time

def main():
    # Récupération des arguments passés au script
    parser = argparse.ArgumentParser(description="Capture de paquets avec tcpdump")
    parser.add_argument("--interface", default="any")
    parser.add_argument("--duration", type=float, default=20.0)
    parser.add_argument("--output", required=True)
    parser.add_argument("--filter", default="net 10.0.0.0/24")
    args = parser.parse_args()

    # Construction de la commande tcpdump
    command = [
        "tcpdump",
        "-i",
        args.interface,
        "-w",
        args.output,
        *shlex.split(args.filter),
    ]

    # Lancement de la capture réseau
    process = subprocess.Popen(command)
    try:
        # Attente pendant la durée demandée
        time.sleep(args.duration)
    finally:
        # Arrêt propre de tcpdump pour sauvegarder correctement le fichier pcap
        process.send_signal(signal.SIGINT)
        process.wait()

if __name__ == "__main__":
    main()
