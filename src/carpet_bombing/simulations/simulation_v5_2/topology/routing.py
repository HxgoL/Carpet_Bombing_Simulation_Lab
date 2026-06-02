from carpet_bombing.simulations.simulation_v5_2.config.settings import (
    ATLANTIC_CANADA_LINK,
    CANADA_GATEWAY,
    PARIS_GATEWAY,
    PARIS_TRANSIT_LINK,
)


def configure_routes(routers, attackers, victims, services):
    r_paris = routers["paris"]
    r_atlantic = routers["atlantic"]
    r_canada = routers["canada"]

    r_paris.setIP(f"{PARIS_GATEWAY}/24", intf="r_paris-eth0")
    r_paris.setIP(PARIS_TRANSIT_LINK["paris_ip"], intf="r_paris-eth1")
    r_atlantic.setIP(PARIS_TRANSIT_LINK["atlantic_ip"], intf="r_atlantic-eth0")
    r_atlantic.setIP(ATLANTIC_CANADA_LINK["atlantic_ip"], intf="r_atlantic-eth1")
    r_canada.setIP(ATLANTIC_CANADA_LINK["canada_ip"], intf="r_canada-eth0")
    r_canada.setIP(f"{CANADA_GATEWAY}/24", intf="r_canada-eth1")

    r_paris.cmd(f"ip route replace 10.20.0.0/24 via {PARIS_TRANSIT_LINK['atlantic_next_hop']}")
    r_atlantic.cmd("ip route replace 10.10.0.0/24 via 172.16.0.1")
    r_atlantic.cmd(f"ip route replace 10.20.0.0/24 via {ATLANTIC_CANADA_LINK['canada_next_hop']}")
    r_canada.cmd(f"ip route replace 10.10.0.0/24 via {ATLANTIC_CANADA_LINK['atlantic_next_hop']}")

    for attacker in attackers:
        attacker.cmd(f"ip route replace default via {PARIS_GATEWAY}")

    for host in [*victims, *services]:
        host.cmd(f"ip route replace default via {CANADA_GATEWAY}")
