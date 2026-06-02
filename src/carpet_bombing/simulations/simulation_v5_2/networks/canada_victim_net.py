from carpet_bombing.simulations.simulation_v5_2.config.settings import (
    ACTIVE_VICTIM_IPS,
    CANADA_GATEWAY,
)


def build_canada_victim_net(net, router):
    switch = net.addSwitch("s_canada")
    net.addLink(
        router,
        switch,
        intfName1="r_canada-eth1",
        params1={"ip": f"{CANADA_GATEWAY}/24"},
        bw=10,
        delay="8ms",
    )

    victims = [
        net.addHost(
            f"h{index}",
            ip=f"{ip_address}/24",
            defaultRoute=f"via {CANADA_GATEWAY}",
        )
        for index, ip_address in enumerate(ACTIVE_VICTIM_IPS, start=1)
    ]

    for victim in victims:
        net.addLink(victim, switch)

    return {"switch": switch, "hosts": victims}
