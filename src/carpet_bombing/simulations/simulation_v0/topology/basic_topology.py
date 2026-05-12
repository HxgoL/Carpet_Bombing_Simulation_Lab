from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel

def run():
    # Création d'un réseau Mininet sans contrôleur SDN
    # OVSBridge permet d'utiliser un switch virtuel simple
    net = Mininet(controller=None, switch=OVSBridge)

    # Création du switch virtuel central
    switch = net.addSwitch("s1")

    # Création de 8 hôtes : h1 à h8
    # Chaque hôte reçoit une adresse IP dans le réseau 10.0.0.0/24
    for i in range(1, 9):
        host = net.addHost(f"h{i}", ip=f"10.0.0.{i}/24")

        # Connexion de chaque hôte au switch
        net.addLink(host, switch)

    # Démarrage du réseau simulé
    net.start()

    # Ouverture de la console Mininet pour tester la topologie
    # Exemples de commandes : net, pingall, h1 ip addr
    CLI(net)

    # Arrêt propre du réseau quand on quitte la console
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    run()
