from pathlib import Path
import argparse
import time
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

ATTACKER_INFOS = [
    ("a1", "10.0.1.1", "10.0.1.254"),
    ("a2", "10.0.1.2", "10.0.1.254"),
    ("a3", "10.0.2.1", "10.0.2.254"),
    ("a4", "10.0.2.2", "10.0.2.254"),
]
SIMULATED_SOURCE_RANGES = [
    "192.0.2.10-192.0.2.80",
    "198.51.100.20-198.51.100.90",
    "203.0.113.30-203.0.113.100",
    "198.18.0.10-198.18.0.80",
]
ACTIVE_VICTIM_IPS = [
    "10.0.0.1",
    "10.0.0.2",
    "10.0.0.3",
    "10.0.0.4",
    "10.0.0.5",
    "10.0.0.8",
    "10.0.0.13",
    "10.0.0.19",
    "10.0.0.21",
    "10.0.0.34",
    "10.0.0.41",
    "10.0.0.42",
    "10.0.0.50",
    "10.0.0.51",
    "10.0.0.57",
    "10.0.0.60",
    "10.0.0.61",
    "10.0.0.70",
    "10.0.0.75",
    "10.0.0.80",
]
VICTIM_GATEWAY = "10.0.0.254"
ATTACK_TARGET_RANGES = ["10.0.0.1-10.0.0.20", "10.0.0.21-10.0.0.40", "10.0.0.41-10.0.0.60", "10.0.0.61-10.0.0.80"]
SINGLE_TARGET_IP = "10.0.0.1"
VICTIM_LINK_BW = 5
VICTIM_LINK_DELAY = "10ms"
VICTIM_LINK_LOSS = 0
ROUTER_LINK_DELAY = "5ms"

def parse_args():
    parser = argparse.ArgumentParser(description="Run the V5 Mininet topology.")
    parser.add_argument("--auto-scenario", choices=["normal", "single_target", "carpet"])
    parser.add_argument("--duration", type=int, default=45)
    parser.add_argument("--attack-duration", type=int, default=30)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--pps", type=int, default=120)
    parser.add_argument("--protocol", choices=["icmp", "udp", "tcp_syn", "dns_amp", "mixed"], default="mixed")
    parser.add_argument("--fragment-mode", choices=["manual", "auto", "none"], default="manual")
    return parser.parse_args()

class LinuxRouter(Node):
    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()

def configure_routes(r1, r2, rcore, gw, attackers, victims):
    for attacker in attackers:
        attacker.cmd(f"ip route replace default via {attacker.params['gateway']}")

    for victim in victims:
        victim.cmd(f"ip route replace default via {VICTIM_GATEWAY}")

    r1.cmd("ip route replace 10.0.0.0/24 via 10.10.1.2")
    r1.cmd("ip route replace 10.0.2.0/24 via 10.10.1.2")
    r2.cmd("ip route replace 10.0.0.0/24 via 10.10.2.2")
    r2.cmd("ip route replace 10.0.1.0/24 via 10.10.2.2")
    rcore.cmd("ip route replace 10.0.1.0/24 via 10.10.1.1")
    rcore.cmd("ip route replace 10.0.2.0/24 via 10.10.2.1")
    rcore.cmd("ip route replace 10.0.0.0/24 via 10.10.3.2")
    gw.cmd("ip route replace 10.0.1.0/24 via 10.10.3.1")
    gw.cmd("ip route replace 10.0.2.0/24 via 10.10.3.1")

def run(auto_scenario=None, duration=45, attack_duration=30, warmup=5, pps=120, protocol="mixed", fragment_mode="manual"):
    net = Mininet(controller=None, switch=OVSBridge, link=TCLink)

    attacker_switch_1 = net.addSwitch("s1")
    attacker_switch_2 = net.addSwitch("s2")
    victim_switch = net.addSwitch("s3")

    r1 = net.addHost("r1", cls=LinuxRouter)
    r2 = net.addHost("r2", cls=LinuxRouter)
    rcore = net.addHost("r_core", cls=LinuxRouter)
    gw = net.addHost("gw", cls=LinuxRouter)

    net.addLink(r1, attacker_switch_1, intfName1="r1-eth0", params1={"ip": "10.0.1.254/24"})
    net.addLink(r2, attacker_switch_2, intfName1="r2-eth0", params1={"ip": "10.0.2.254/24"})

    net.addLink(r1, rcore, intfName1="r1-eth1", intfName2="r_core-eth0", params1={"ip": "10.10.1.1/30"}, params2={"ip": "10.10.1.2/30"}, delay=ROUTER_LINK_DELAY)
    net.addLink(r2, rcore, intfName1="r2-eth1", intfName2="r_core-eth1", params1={"ip": "10.10.2.1/30"}, params2={"ip": "10.10.2.2/30"}, delay=ROUTER_LINK_DELAY)
    net.addLink(rcore, gw, intfName1="r_core-eth2", intfName2="gw-eth0", params1={"ip": "10.10.3.1/30"}, params2={"ip": "10.10.3.2/30"}, delay=ROUTER_LINK_DELAY)

    net.addLink(
        gw,
        victim_switch,
        intfName1="gw-eth1",
        params1={"ip": f"{VICTIM_GATEWAY}/24"},
        bw=VICTIM_LINK_BW,
        delay=VICTIM_LINK_DELAY,
        loss=VICTIM_LINK_LOSS,
    )

    attackers = []
    for name, ip_address, gateway in ATTACKER_INFOS:
        attacker = net.addHost(name, ip=f"{ip_address}/24", defaultRoute=f"via {gateway}")
        attacker.params["gateway"] = gateway
        attackers.append(attacker)

    victims = [
        net.addHost(
            f"h{index}",
            ip=f"{ip_address}/24",
            defaultRoute=f"via {VICTIM_GATEWAY}",
        )
        for index, ip_address in enumerate(ACTIVE_VICTIM_IPS, start=1)
    ]

    for attacker in attackers[:2]:
        net.addLink(attacker, attacker_switch_1)
    for attacker in attackers[2:]:
        net.addLink(attacker, attacker_switch_2)

    for victim in victims:
        net.addLink(victim, victim_switch)

    net.start()

    r1.setIP("10.0.1.254/24", intf="r1-eth0")
    r1.setIP("10.10.1.1/30", intf="r1-eth1")
    r2.setIP("10.0.2.254/24", intf="r2-eth0")
    r2.setIP("10.10.2.1/30", intf="r2-eth1")
    rcore.setIP("10.10.1.2/30", intf="r_core-eth0")
    rcore.setIP("10.10.2.2/30", intf="r_core-eth1")
    rcore.setIP("10.10.3.1/30", intf="r_core-eth2")
    gw.setIP("10.10.3.2/30", intf="gw-eth0")
    gw.setIP(f"{VICTIM_GATEWAY}/24", intf="gw-eth1")
    configure_routes(r1, r2, rcore, gw, attackers, victims)

    normal_script = Path(__file__).resolve().parents[1] / "traffic_generator" / "normal_traffic.py"
    receiver_script = Path(__file__).resolve().parents[1] / "traffic_generator" / "packet_receiver.py"
    attack_script = Path(__file__).resolve().parents[1] / "traffic_generator" / "advanced_carpet_bombing_attack.py"

    for victim in victims:
        victim.cmd(f"python3 {receiver_script} > /tmp/{victim.name}_packet_receiver_v5.log 2>&1 &")

    for index, victim in enumerate(victims, start=1):
        peers = ",".join(v.IP() for v in victims if v != victim)
        min_delay = 3 + index % 5
        max_delay = min_delay + 5
        victim.cmd(
            f"python3 {normal_script} --peers {peers} "
            f"--min-delay {min_delay} --max-delay {max_delay} "
            f"> /tmp/{victim.name}_normal_traffic_v5.log 2>&1 &"
        )

    print("\nSimulation V5.3 : topologie multi-routeurs + récepteurs TCP/UDP")
    print("  Scénarios : normal, single_target, carpet")
    print("  Chemin : attaquants -> r1/r2 -> r_core -> gw -> victimes")
    print(f"  Lien victime : {VICTIM_LINK_BW} Mbit/s, {VICTIM_LINK_DELAY}, perte {VICTIM_LINK_LOSS}%")
    print(f"  Attaque : {pps} pps, protocole {protocol}, fragmentation {fragment_mode}")
    print("\nCommandes de test :")
    print("  a1 traceroute 10.0.0.1")
    print("  start_single_target_attack")
    print("  start_carpet_attack")
    print("  stop_attack")
    print("  gw tc -s qdisc show dev gw-eth1")
    print()

    def launch_attack(name, destination_args):
        for attacker, source_range, destination_arg in zip(attackers, SIMULATED_SOURCE_RANGES, destination_args):
            attacker.cmd(
                f"timeout {attack_duration} python3 {attack_script} "
                f"{destination_arg} "
                f"--src-range {source_range} "
                f"--duration {attack_duration} "
                f"--pps {pps} "
                f"--protocol {protocol} "
                f"--payload-size 4000 "
                f"--fragment-mode {fragment_mode} "
                f"--fragsize 300 "
                f"--ttl-min 40 "
                f"--ttl-max 64 "
                f"--src-rotation-interval 5 "
                f"> /tmp/{attacker.name}_{name}_attack_v5_3.log 2>&1 &"
            )

    def launch_single_target_attack():
        launch_attack("single_target", [f"--dst-ip {SINGLE_TARGET_IP}"] * len(attackers))
        print(f"Attaque single-target V5.3 lancée pendant {attack_duration} secondes")

    def launch_carpet_attack():
        launch_attack("carpet", [f"--dst-range {target_range}" for target_range in ATTACK_TARGET_RANGES])
        print(f"Attaque carpet bombing V5.3 lancée pendant {attack_duration} secondes")

    def kill_attack():
        for attacker in attackers:
            attacker.cmd("pkill -f advanced_carpet_bombing_attack.py")

    def start_single_target_attack(_self, _line):
        launch_single_target_attack()

    def start_carpet_attack(_self, _line):
        launch_carpet_attack()

    def stop_attack(_self, _line):
        kill_attack()
        print("Attaque V5.3 arrêtée")

    CLI.do_start_single_target_attack = start_single_target_attack
    CLI.do_start_carpet_attack = start_carpet_attack
    CLI.do_stop_attack = stop_attack

    if auto_scenario == "normal":
        print(f"Scénario normal automatique pendant {duration} secondes")
        time.sleep(duration)
    elif auto_scenario == "single_target":
        print(f"Scénario DDoS single-target : warmup {warmup}s puis attaque")
        time.sleep(warmup)
        launch_single_target_attack()
        time.sleep(max(duration - warmup, 0))
        kill_attack()
    elif auto_scenario == "carpet":
        print(f"Scénario carpet bombing : warmup {warmup}s puis attaque")
        time.sleep(warmup)
        launch_carpet_attack()
        time.sleep(max(duration - warmup, 0))
        kill_attack()
    else:
        CLI(net)

    for victim in victims:
        victim.cmd("pkill -f normal_traffic.py")
        victim.cmd("pkill -f packet_receiver.py")
    for attacker in attackers:
        attacker.cmd("pkill -f advanced_carpet_bombing_attack.py")

    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    args = parse_args()
    run(
        auto_scenario=args.auto_scenario,
        duration=args.duration,
        attack_duration=args.attack_duration,
        warmup=args.warmup,
        pps=args.pps,
        protocol=args.protocol,
        fragment_mode=args.fragment_mode,
    )
