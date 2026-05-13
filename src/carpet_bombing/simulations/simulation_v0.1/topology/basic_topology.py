from pathlib import Path
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel

HOST_COUNT = 8

def run():
    # Création d'un réseau Mininet sans contrôleur SDN
    # OVSBridge permet d'utiliser un switch virtuel simple
    net = Mininet(controller=None, switch=OVSBridge)

    # Création du switch virtuel central
    switch = net.addSwitch("s1")

    # Création de 8 hôtes : h1 à h8
    # Chaque hôte reçoit une adresse IP dans le réseau 10.0.0.0/24
    hosts = [
        net.addHost(f"h{i}", ip=f"10.0.0.{i}/24")
        for i in range(1, HOST_COUNT + 1)
    ]

    # Connexion de chaque hôte au switch
    for host in hosts:
        net.addLink(host, switch)

    # Démarrage du réseau simulé
    net.start()

    # Récupération automatique du chemin vers le générateur de trafic Scapy
    script = Path(__file__).resolve().parents[1] / "traffic_generator" / "basic_scapy_traffic.py"

    # Lancement du trafic sur chaque hôte vers les autres
    # Logs : /tmp/hX_traffic.log
    # & = exécution en arrière-plan
    for host in hosts:
        peers = ",".join(h.IP() for h in hosts if h != host)
        host.cmd(f"python3 {script} --peers {peers} > /tmp/{host.name}_traffic.log 2>&1 &")

    # Ouverture de la console Mininet pour tester la topologie
    # Exemples de commandes : net, pingall, h1 ip addr
    CLI(net)

    # Arrêt du générateur de trafic lancé en arrière-plan sur chaque hôte
    for host in hosts:
        host.cmd("pkill -f basic_scapy_traffic.py")

    # Arrêt propre du réseau quand on quitte la console
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    run()
