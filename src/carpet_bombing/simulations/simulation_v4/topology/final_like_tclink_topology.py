from pathlib import Path
import argparse
import subprocess
import time
from carpet_bombing.simulations.simulation_v4.topology.ServiceTopology import API_IMAGE, build_api_image
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

from containernet.net import Containernet
from containernet.node import Docker

ATTACKER_COUNT = 4
ACTIVE_VICTIM_IPS = [
    "10.0.0.1",
    "10.0.0.2",
    "10.0.0.3",
    "10.0.0.4",
    "10.0.0.5",
    "10.0.0.21",
    "10.0.0.22",
    "10.0.0.23",
    "10.0.0.24",
    "10.0.0.25",
    "10.0.0.41",
    "10.0.0.42",
    "10.0.0.43",
    "10.0.0.44",
    "10.0.0.45",
    "10.0.0.61",
    "10.0.0.62",
    "10.0.0.63",
    "10.0.0.64",
    "10.0.0.65",
]
VICTIM_GATEWAY = "10.0.0.254"
ATTACKER_GATEWAY = "10.0.1.254"
ATTACK_TARGET_RANGES = ["10.0.0.1-10.0.0.20", "10.0.0.21-10.0.0.40", "10.0.0.41-10.0.0.60", "10.0.0.61-10.0.0.80"]

# Paramètres du lien limité entre la gateway et le réseau victime.
# Ce lien est conservé depuis la V2 pour observer la congestion.
VICTIM_LINK_BW = 5
VICTIM_LINK_DELAY = "10ms"
VICTIM_LINK_LOSS = 0



def parse_args():
    parser = argparse.ArgumentParser(description="Run the V4 Mininet topology.")
    parser.add_argument("--auto-scenario", choices=["normal", "attack"])
    parser.add_argument("--duration", type=int, default=45)
    parser.add_argument("--attack-duration", type=int, default=30)
    parser.add_argument("--warmup", type=int, default=5)
    return parser.parse_args()


class LinuxGateway(Node):
    def config(self, **params):
        super().config(**params)
        # Activation du routage IP pour faire passer le trafic entre les deux sous-réseaux
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        # Désactivation du routage IP quand Mininet s'arrête
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()




def run(auto_scenario=None, duration=45, attack_duration=30, warmup=5):
    build_api_image()

    # Création d'un réseau Mininet sans contrôleur SDN
    # link=TCLink permet d'ajouter des contraintes de bande passante, délai et perte
    net = Containernet(controller=None, switch=OVSBridge, link=TCLink)

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

    # Création des victimes actives réparties dans le sous-réseau 10.0.0.0/24
    victims = [
        net.addHost(
            f"h{index}",
            ip=f"{ip_address}/24",
            defaultRoute=f"via {VICTIM_GATEWAY}",
        )
        for index, ip_address in enumerate(ACTIVE_VICTIM_IPS, start=1)
    ]

    # Création de serveurs docker

    nginx_server = net.addDocker(
        "srv_nginx",
        ip="10.0.0.12/24",
        dimage="nginx:alpine",
        defaultRoute=f"via {VICTIM_GATEWAY}",
    )

    dns_server = net.addDocker(
        "srv_dns",
        ip="10.0.0.13/24",
        dimage="internetsystemsconsortium/bind9:9.18",
        defaultRoute=f"via {VICTIM_GATEWAY}",
    )

    api_server = net.addDocker(
        "srv_api",
        ip="10.0.0.14/24",
        dimage=API_IMAGE,
        defaultRoute=f"via {VICTIM_GATEWAY}",
    )

    # Connexion des attaquants à leur switch
    for attacker in attackers:
        net.addLink(attacker, attacker_switch)

    # Connexion des victimes à leur switch
    for victim in victims:
        net.addLink(victim, victim_switch)


    for server in [nginx_server, dns_server, api_server]:
        net.addLink(server, victim_switch)

    #####

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
    # Logs : /tmp/victimX_normal_traffic_v4.log
    # & = exécution en arrière-plan
    for index, victim in enumerate(victims, start=1):
        peers = ",".join(v.IP() for v in victims if v != victim)
        min_delay = 3 + index % 5
        max_delay = min_delay + 5
        victim.cmd(
            f"python3 {normal_script} --peers {peers} "
            f"--min-delay {min_delay} --max-delay {max_delay} "
            f"> /tmp/{victim.name}_normal_traffic_v4.log 2>&1 &"
        )

    print("\nSimulation V4 : topologie élargie + captures reproductibles")
    print(f"  Attaquants : {ATTACKER_COUNT}")
    print("  Victimes actives : 20 hôtes répartis entre 10.0.0.1 et 10.0.0.65")
    print("  IP ciblées : 10.0.0.1-10.0.0.80")
    print("  IP inactives ciblées : IP ciblées non créées dans Mininet")
    print("  Cibles par attaquant :")
    for attacker, target_range in zip(attackers, ATTACK_TARGET_RANGES):
        print(f"    {attacker.name} -> {target_range}")
    print(f"  Lien gateway -> victimes : {VICTIM_LINK_BW} Mbit/s, délai {VICTIM_LINK_DELAY}, perte {VICTIM_LINK_LOSS}%")
    print("\nCommandes de test :")
    print("  a1 ping -c 3 10.0.0.1")
    print("  start_attack")
    print("  stop_attack")
    print("  gw tc -s qdisc show dev gw-eth1")
    print("  mode automatique : --auto-scenario normal ou --auto-scenario attack")
    print()

    def launch_attack():
        for attacker, target_range in zip(attackers, ATTACK_TARGET_RANGES):
            attacker.cmd(
                f"timeout {attack_duration} python3 {attack_script} "
                f"--targets {target_range} "
                f"--packet-count 1000000 "
                f"--delay 0 "
                f"--payload-size 1024 "
                f"--protocol UDP "
                f"> /tmp/{attacker.name}_carpet_attack_v4.log 2>&1 &"
            )
        print(f"Attaque V4 lancée pendant {attack_duration} secondes")

    def kill_attack():
        for attacker in attackers:
            attacker.cmd("pkill -f carpet_bombing_attack.py")

    # Commandes personnalisées disponibles dans la console Mininet
    def start_attack(_self, _line):
        launch_attack()

    def stop_attack(_self, _line):
        kill_attack()
        print("Attaque V4 arrêtée")

    CLI.do_start_attack = start_attack
    CLI.do_stop_attack = stop_attack

    if auto_scenario == "normal":
        print(f"Scénario normal automatique pendant {duration} secondes")
        time.sleep(duration)
    elif auto_scenario == "attack":
        print(f"Scénario attaque automatique : warmup {warmup}s puis attaque")
        time.sleep(warmup)
        launch_attack()
        time.sleep(max(duration - warmup, 0))
        kill_attack()
    else:
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
    args = parse_args()
    run(args.auto_scenario, args.duration, args.attack_duration, args.warmup)
