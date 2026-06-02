from carpet_bombing.simulations.simulation_v5_2.config.settings import CANADA_GATEWAY


def build_canada_services(net, switch):
    web_server = net.addDocker(
        "ca_web",
        ip="10.20.0.90/24",
        dimage="nginx:alpine",
        defaultRoute=f"via {CANADA_GATEWAY}",
    )
    api_server = net.addDocker(
        "ca_api",
        ip="10.20.0.91/24",
        dimage="python:3.11-slim",
        defaultRoute=f"via {CANADA_GATEWAY}",
        command="python3 -m http.server 8000",
    )

    for server in [web_server, api_server]:
        net.addLink(server, switch)

    return [web_server, api_server]
