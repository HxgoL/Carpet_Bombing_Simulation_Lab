from pathlib import Path
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

VICTIM_COUNT = 8
VICTIM_GATEWAY = "10.0.0.254"
ATTACKER_GATEWAY = "10.0.1.254"

# Paramètres du lien limité entre la gateway et le réseau victime.
# Ce lien sert à créer un goulot d'étranglement pour observer la congestion.
VICTIM_LINK_BW = 5
VICTIM_LINK_DELAY = "10ms"
VICTIM_LINK_LOSS = 0


class LinuxGateway(Node):
    def config(self, **params):
        super().config(**params)
        # Activation du routage IP pour faire passer le trafic entre les deux sous-réseaux
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        # Désactivation du routage IP quand Mininet s'arrête
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


def run():
    # Création d'un réseau Mininet sans contrôleur SDN
    # link=TCLink permet d'ajouter des contraintes de bande passante, délai et perte
    net = Mininet(controller=None, switch=OVSBridge, link=TCLink)

    # Création des deux switchs : s1 côté attaquant, s2 côté victimes
    attacker_switch = net.addSwitch("s1")
    victim_switch = net.addSwitch("s2")

    # Création de la gateway entre les deux sous-réseaux
    gateway = net.addHost("gw", cls=LinuxGateway)

    # Connexion de la gateway au sous-réseau attaquant
    net.addLink(
        gateway,
        attacker_switch,
        intfName1="gw-eth0",
        params1={"ip": f"{ATTACKER_GATEWAY}/24"},
    )

    # Connexion de la gateway au sous-réseau victime avec TCLink
    # Le trafic vers les victimes passe par ce lien limité.
    net.addLink(
        gateway,
        victim_switch,
        intfName1="gw-eth1",
        params1={"ip": f"{VICTIM_GATEWAY}/24"},
        bw=VICTIM_LINK_BW,
        delay=VICTIM_LINK_DELAY,
        loss=VICTIM_LINK_LOSS,
    )

    # Création de l'attaquant dans le sous-réseau 10.0.1.0/24
    attacker = net.addHost(
        "a1",
        ip="10.0.1.1/24",
        defaultRoute=f"via {ATTACKER_GATEWAY}",
    )

    # Création des victimes dans le sous-réseau 10.0.0.0/24
    victims = [
        net.addHost(
            f"h{i}",
            ip=f"10.0.0.{i}/24",
            defaultRoute=f"via {VICTIM_GATEWAY}",
        )
        for i in range(1, VICTIM_COUNT + 1)
    ]

    # Connexion de l'attaquant à son switch
    net.addLink(attacker, attacker_switch)

    # Connexion des victimes à leur switch
    for victim in victims:
        net.addLink(victim, victim_switch)

    # Démarrage du réseau simulé
    net.start()

    # Configuration explicite des interfaces de la gateway
    gateway.setIP(f"{ATTACKER_GATEWAY}/24", intf="gw-eth0")
    gateway.setIP(f"{VICTIM_GATEWAY}/24", intf="gw-eth1")

    # Ajout explicite des routes entre les deux sous-réseaux
    attacker.cmd(f"ip route replace default via {ATTACKER_GATEWAY}")
    for victim in victims:
        victim.cmd(f"ip route replace default via {VICTIM_GATEWAY}")

    # Récupération automatique du chemin vers le générateur de trafic normal
    normal_script = Path(__file__).resolve().parents[1] / "traffic_generator" / "normal_traffic.py"

    # Récupération automatique du chemin vers le générateur d'attaque
    attack_script = Path(__file__).resolve().parents[1] / "traffic_generator" / "carpet_bombing_attack.py"

    # Lancement du trafic normal entre les victimes
    # Logs : /tmp/victimX_normal_traffic_v2.log
    # & = exécution en arrière-plan
    for index, victim in enumerate(victims, start=1):
        peers = ",".join(v.IP() for v in victims if v != victim)
        min_delay = 3 + index
        max_delay = min_delay + 5
        victim.cmd(
            f"python3 {normal_script} --peers {peers} "
            f"--min-delay {min_delay} --max-delay {max_delay} "
            f"> /tmp/{victim.name}_normal_traffic_v2.log 2>&1 &"
        )

    print("\nSimulation V2 : gateway + TCLink côté victimes")
    print(f"  Lien gateway -> victimes : {VICTIM_LINK_BW} Mbit/s, délai {VICTIM_LINK_DELAY}, perte {VICTIM_LINK_LOSS}%")
    print("\nCommandes de test :")
    print("  a1 ping -c 10 10.0.0.1")
    print("  iperf3 peut être ajouté plus tard pour mesurer le débit utile")
    print(f"  a1 python3 {attack_script}")
    print()

    # Ouverture de la console Mininet pour tester la topologie
    CLI(net)

    # Arrêt du générateur de trafic normal lancé en arrière-plan sur chaque victime
    for victim in victims:
        victim.cmd("pkill -f normal_traffic.py")

    # Arrêt propre du réseau quand on quitte la console
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
