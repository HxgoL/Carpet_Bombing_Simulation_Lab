from carpet_bombing.simulations.simulation_v5_2.config.settings import (
    ATLANTIC_CANADA_LINK,
    PARIS_TRANSIT_LINK,
)
from carpet_bombing.simulations.simulation_v5_2.nodes.routers import LinuxRouter


def build_transit_routers(net):
    r_paris = net.addHost("r_paris", cls=LinuxRouter)
    r_atlantic = net.addHost("r_atlantic", cls=LinuxRouter)
    r_canada = net.addHost("r_canada", cls=LinuxRouter)

    net.addLink(
        r_paris,
        r_atlantic,
        intfName1="r_paris-eth1",
        intfName2="r_atlantic-eth0",
        params1={"ip": PARIS_TRANSIT_LINK["paris_ip"]},
        params2={"ip": PARIS_TRANSIT_LINK["atlantic_ip"]},
        bw=PARIS_TRANSIT_LINK["bw"],
        delay=PARIS_TRANSIT_LINK["delay"],
    )
    net.addLink(
        r_atlantic,
        r_canada,
        intfName1="r_atlantic-eth1",
        intfName2="r_canada-eth0",
        params1={"ip": ATLANTIC_CANADA_LINK["atlantic_ip"]},
        params2={"ip": ATLANTIC_CANADA_LINK["canada_ip"]},
        bw=ATLANTIC_CANADA_LINK["bw"],
        delay=ATLANTIC_CANADA_LINK["delay"],
        loss=ATLANTIC_CANADA_LINK["loss"],
    )

    return {"paris": r_paris, "atlantic": r_atlantic, "canada": r_canada}
