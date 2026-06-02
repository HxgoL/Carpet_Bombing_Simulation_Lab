from carpet_bombing.simulations.simulation_v5_2.config.settings import (
    ATTACKER_COUNT,
    PARIS_GATEWAY,
)


def build_paris_attacker_net(net, router):
    switch = net.addSwitch("s_paris")
    net.addLink(
        router,
        switch,
        intfName1="r_paris-eth0",
        params1={"ip": f"{PARIS_GATEWAY}/24"},
        bw=100,
        delay="2ms",
    )

    attackers = [
        net.addHost(
            f"a{i}",
            ip=f"10.10.0.{i}/24",
            defaultRoute=f"via {PARIS_GATEWAY}",
        )
        for i in range(1, ATTACKER_COUNT + 1)
    ]

    for attacker in attackers:
        net.addLink(attacker, switch)

    return {"switch": switch, "hosts": attackers}
