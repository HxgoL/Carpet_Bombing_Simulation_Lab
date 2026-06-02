import argparse
import sys
import time
from pathlib import Path

from containernet.net import Containernet
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import OVSBridge

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from carpet_bombing.simulations.simulation_v5_2.attacks.orchestrator import (
    launch_fragmented_carpet_attack,
    launch_single_target_attack,
    stop_fragmented_carpet_attack,
)
from carpet_bombing.simulations.simulation_v5_2.config.settings import (
    ATTACK_TARGET_RANGE,
    DEFAULT_ATTACK_DURATION,
    DEFAULT_DURATION,
    DEFAULT_FRAGMENT_MODE,
    DEFAULT_PPS,
    DEFAULT_PROTOCOL,
    DEFAULT_WARMUP,
    SINGLE_TARGET_IP,
)
from carpet_bombing.simulations.simulation_v5_2.networks.canada_victim_net import (
    build_canada_victim_net,
)
from carpet_bombing.simulations.simulation_v5_2.networks.paris_attacker_net import (
    build_paris_attacker_net,
)
from carpet_bombing.simulations.simulation_v5_2.networks.transit_net import (
    build_transit_routers,
)
from carpet_bombing.simulations.simulation_v5_2.services.canada_services import (
    build_canada_services,
)
from carpet_bombing.simulations.simulation_v5_2.topology.cleanup import cleanup_processes
from carpet_bombing.simulations.simulation_v5_2.topology.routing import configure_routes
from carpet_bombing.simulations.simulation_v5_2.traffic.normal_users import (
    start_normal_traffic,
    start_receivers,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run the V5 Paris-Canada fragmented topology.")
    parser.add_argument("--auto-scenario", choices=["normal", "single_target", "carpet"])
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    parser.add_argument("--attack-duration", type=int, default=DEFAULT_ATTACK_DURATION)
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP)
    parser.add_argument("--pps", type=int, default=DEFAULT_PPS)
    parser.add_argument(
        "--protocol",
        choices=["icmp", "udp", "tcp_syn", "dns_amp", "mixed"],
        default=DEFAULT_PROTOCOL,
    )
    parser.add_argument("--fragment-mode", choices=["manual", "auto", "none"], default=DEFAULT_FRAGMENT_MODE)
    return parser.parse_args()


def run(
    auto_scenario=None,
    duration=DEFAULT_DURATION,
    attack_duration=DEFAULT_ATTACK_DURATION,
    warmup=DEFAULT_WARMUP,
    pps=DEFAULT_PPS,
    protocol=DEFAULT_PROTOCOL,
    fragment_mode=DEFAULT_FRAGMENT_MODE,
):
    net = Containernet(controller=None, switch=OVSBridge, link=TCLink)

    routers = build_transit_routers(net)
    paris_net = build_paris_attacker_net(net, routers["paris"])
    canada_net = build_canada_victim_net(net, routers["canada"])
    services = build_canada_services(net, canada_net["switch"])

    attackers = paris_net["hosts"]
    victims = canada_net["hosts"]

    net.start()
    configure_routes(routers, attackers, victims, services)
    start_receivers(victims)
    start_normal_traffic(victims)

    print("\nSimulation V5.2 : Paris -> transit -> Canada + trafic avancé")
    print("  Scénarios : normal, single_target, carpet")
    print(f"  Attaquants Paris : {len(attackers)}")
    print("  Victimes Canada actives : 20 hôtes dans 10.20.0.0/24")
    print(f"  Cible single-target : {SINGLE_TARGET_IP}")
    print(f"  Plage ciblée : {ATTACK_TARGET_RANGE}")
    print("  Route attendue : a1 -> r_paris -> r_atlantic -> r_canada -> victime")
    print("  Test traceroute : a1 traceroute -n 10.20.0.10")
    print("  Commandes : start_single_target_attack, start_carpet_attack, stop_attack, show_route")
    print()

    def launch_single_target():
        launch_single_target_attack(
            attackers=attackers,
            attack_duration=attack_duration,
            pps=pps,
            protocol=protocol,
            fragment_mode=fragment_mode,
        )
        print(f"Attaque single-target V5.2 lancée pendant {attack_duration} secondes")

    def launch_carpet():
        launch_fragmented_carpet_attack(
            attackers=attackers,
            attack_duration=attack_duration,
            pps=pps,
            protocol=protocol,
            fragment_mode=fragment_mode,
        )
        print(f"Attaque carpet bombing V5.2 lancée pendant {attack_duration} secondes")

    def kill_attack():
        stop_fragmented_carpet_attack(attackers)

    def start_single_target_attack(_self, _line):
        launch_single_target()

    def start_carpet_attack(_self, _line):
        launch_carpet()

    def stop_attack(_self, _line):
        kill_attack()
        print("Attaque V5 arrêtée")

    def show_route(_self, _line):
        print(
            attackers[0].cmd(
                "traceroute -n 10.20.0.10 2>/dev/null "
                "|| tracepath -n 10.20.0.10 2>/dev/null "
                "|| ip route get 10.20.0.10"
            )
        )

    CLI.do_start_single_target_attack = start_single_target_attack
    CLI.do_start_carpet_attack = start_carpet_attack
    CLI.do_stop_attack = stop_attack
    CLI.do_show_route = show_route

    if auto_scenario == "normal":
        print(f"Scénario normal automatique pendant {duration} secondes")
        time.sleep(duration)
    elif auto_scenario == "single_target":
        print(f"Scénario DDoS single-target : warmup {warmup}s puis attaque")
        time.sleep(warmup)
        launch_single_target()
        time.sleep(max(duration - warmup, 0))
        kill_attack()
    elif auto_scenario == "carpet":
        print(f"Scénario carpet bombing : warmup {warmup}s puis attaque")
        time.sleep(warmup)
        launch_carpet()
        time.sleep(max(duration - warmup, 0))
        kill_attack()
    else:
        CLI(net)

    cleanup_processes(attackers, victims)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    args = parse_args()
    run(
        args.auto_scenario,
        args.duration,
        args.attack_duration,
        args.warmup,
        args.pps,
        args.protocol,
        args.fragment_mode,
    )
