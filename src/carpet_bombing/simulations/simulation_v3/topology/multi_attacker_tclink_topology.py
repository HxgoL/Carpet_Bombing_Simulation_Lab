from pathlib import Path
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

ATTACKER_COUNT = 4
VICTIM_COUNT = 8
VICTIM_GATEWAY = "10.0.0.254"
ATTACKER_GATEWAY = "10.0.1.254"
ATTACK_TARGET_RANGES = ["10.0.0.1-10.0.0.10", "10.0.0.11-10.0.0.20", "10.0.0.21-10.0.0.30", "10.0.0.31-10.0.0.40"]

# Paramètres du lien limité entre la gateway et le réseau victime.
# Ce lien est conservé depuis la V2 pour observer la congestion.
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

    # Création des deux switchs : s1 côté attaquants, s2 côté victimes
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

    # Création de plusieurs attaquants dans le sous-réseau 10.0.1.0/24
    attackers = [
        net.addHost(
            f"a{i}",
            ip=f"10.0.1.{i}/24",
            defaultRoute=f"via {ATTACKER_GATEWAY}",
        )
        for i in range(1, ATTACKER_COUNT + 1)
    ]

    # Création des victimes actives dans le sous-réseau 10.0.0.0/24
    victims = [
        net.addHost(
            f"h{i}",
            ip=f"10.0.0.{i}/24",
            defaultRoute=f"via {VICTIM_GATEWAY}",
        )
        for i in range(1, VICTIM_COUNT + 1)
    ]

    # Connexion des attaquants à leur switch
    for attacker in attackers:
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
    for attacker in attackers:
        attacker.cmd(f"ip route replace default via {ATTACKER_GATEWAY}")
    for victim in victims:
        victim.cmd(f"ip route replace default via {VICTIM_GATEWAY}")

    # Récupération automatique du chemin vers le générateur de trafic normal
    normal_script = Path(__file__).resolve().parents[1] / "traffic_generator" / "normal_traffic.py"

    # Récupération automatique du chemin vers le générateur d'attaque
    attack_script = Path(__file__).resolve().parents[1] / "traffic_generator" / "carpet_bombing_attack.py"

    # Lancement du trafic normal entre les victimes
    # Logs : /tmp/victimX_normal_traffic_v3.log
    # & = exécution en arrière-plan
    for index, victim in enumerate(victims, start=1):
        peers = ",".join(v.IP() for v in victims if v != victim)
        min_delay = 3 + index
        max_delay = min_delay + 5
        victim.cmd(
            f"python3 {normal_script} --peers {peers} "
            f"--min-delay {min_delay} --max-delay {max_delay} "
            f"> /tmp/{victim.name}_normal_traffic_v3.log 2>&1 &"
        )

    print("\nSimulation V3 : plusieurs attaquants + IP inactives + TCLink")
    print(f"  Attaquants : {ATTACKER_COUNT}")
    print("  Victimes actives : 10.0.0.1-10.0.0.8")
    print("  IP inactives ciblées : 10.0.0.9-10.0.0.40")
    print("  Cibles par attaquant :")
    for attacker, target_range in zip(attackers, ATTACK_TARGET_RANGES):
        print(f"    {attacker.name} -> {target_range}")
    print(f"  Lien gateway -> victimes : {VICTIM_LINK_BW} Mbit/s, délai {VICTIM_LINK_DELAY}, perte {VICTIM_LINK_LOSS}%")
    print("\nCommandes de test :")
    print("  a1 ping -c 3 10.0.0.1")
    print("  start_attack")
    print("  stop_attack")
    print("  gw tc -s qdisc show dev gw-eth1")
    print()

    # Commandes personnalisées disponibles dans la console Mininet
    def start_attack(_self, _line):
        for attacker, target_range in zip(attackers, ATTACK_TARGET_RANGES):
            attacker.cmd(
                f"timeout 30 python3 {attack_script} "
                f"--targets {target_range} "
                f"--packet-count 1000000 "
                f"--delay 0 "
                f"--payload-size 1024 "
                f"--protocol UDP "
                f"> /tmp/{attacker.name}_carpet_attack_v3.log 2>&1 &"
            )
        print("Attaque V3 lancée pendant 30 secondes")

    def stop_attack(_self, _line):
        for attacker in attackers:
            attacker.cmd("pkill -f carpet_bombing_attack.py")
        print("Attaque V3 arrêtée")

    CLI.do_start_attack = start_attack
    CLI.do_stop_attack = stop_attack

    # Ouverture de la console Mininet pour tester la topologie
    CLI(net)

    # Arrêt du générateur de trafic normal lancé en arrière-plan sur chaque victime
    for victim in victims:
        victim.cmd("pkill -f normal_traffic.py")
    for attacker in attackers:
        attacker.cmd("pkill -f carpet_bombing_attack.py")

    # Arrêt propre du réseau quand on quitte la console
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
