"""Description déclarative de la topologie V5.3 par défaut."""

from __future__ import annotations

from .defaults import (
    ROUTER_LINK_DELAY,
    VICTIM_LINK_BANDWIDTH_MBPS,
    VICTIM_LINK_DELAY,
    VICTIM_LINK_LOSS_PERCENT,
    VICTIM_GATEWAY,
    VICTIM_SWITCH_NAME,
)

# Les tuples sont préférés aux listes pour éviter les modifications globales.
ATTACKER_DEFINITIONS = (
    {
        "name": "a1",
        "ip_cidr": "10.0.1.1/24",
        "gateway": "10.0.1.254",
        "switch_name": "s1",
        "simulated_source_range": "192.0.2.10-192.0.2.80",
        "carpet_target_range": "10.0.0.1-10.0.0.20",
    },
    {
        "name": "a2",
        "ip_cidr": "10.0.1.2/24",
        "gateway": "10.0.1.254",
        "switch_name": "s1",
        "simulated_source_range": "198.51.100.20-198.51.100.90",
        "carpet_target_range": "10.0.0.21-10.0.0.40",
    },
    {
        "name": "a3",
        "ip_cidr": "10.0.2.1/24",
        "gateway": "10.0.2.254",
        "switch_name": "s2",
        "simulated_source_range": "203.0.113.30-203.0.113.100",
        "carpet_target_range": "10.0.0.41-10.0.0.60",
    },
    {
        "name": "a4",
        "ip_cidr": "10.0.2.2/24",
        "gateway": "10.0.2.254",
        "switch_name": "s2",
        "simulated_source_range": "198.18.0.10-198.18.0.80",
        "carpet_target_range": "10.0.0.61-10.0.0.80",
    },
)


# Ces adresses correspondent uniquement aux victimes réellement actives.
ACTIVE_VICTIM_IPS = (
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
)


# Les routeurs sont distingués des hôtes ordinaires par le builder Mininet.
ROUTER_NAMES = (
    "r1",
    "r2",
    "r_core",
    "gw",
)


SWITCH_NAMES = (
    "s1",
    "s2",
    "s3",
)


# Les liens structurants de la topologie sont décrits ici.
CORE_LINK_DEFINITIONS = (
    {
        "left_node": "r1",
        "right_node": "s1",
        "left_interface": "r1-eth0",
        "left_ip_cidr": "10.0.1.254/24",
    },
    {
        "left_node": "r2",
        "right_node": "s2",
        "left_interface": "r2-eth0",
        "left_ip_cidr": "10.0.2.254/24",
    },
    {
        "left_node": "r1",
        "right_node": "r_core",
        "left_interface": "r1-eth1",
        "right_interface": "r_core-eth0",
        "left_ip_cidr": "10.10.1.1/30",
        "right_ip_cidr": "10.10.1.2/30",
        "delay": ROUTER_LINK_DELAY,
    },
    {
        "left_node": "r2",
        "right_node": "r_core",
        "left_interface": "r2-eth1",
        "right_interface": "r_core-eth1",
        "left_ip_cidr": "10.10.2.1/30",
        "right_ip_cidr": "10.10.2.2/30",
        "delay": ROUTER_LINK_DELAY,
    },
    {
        "left_node": "r_core",
        "right_node": "gw",
        "left_interface": "r_core-eth2",
        "right_interface": "gw-eth0",
        "left_ip_cidr": "10.10.3.1/30",
        "right_ip_cidr": "10.10.3.2/30",
        "delay": ROUTER_LINK_DELAY,
    },
    {
        "left_node": "gw",
        "right_node": VICTIM_SWITCH_NAME,
        "left_interface": "gw-eth1",
        "left_ip_cidr": f"{VICTIM_GATEWAY}/24",
        "bandwidth_mbps": VICTIM_LINK_BANDWIDTH_MBPS,
        "delay": VICTIM_LINK_DELAY,
        "loss_percent": VICTIM_LINK_LOSS_PERCENT,
    },
)


# Routes statiques nécessaires entre les différents sous-réseaux.
ROUTE_DEFINITIONS = (
    {
        "node_name": "r1",
        "destination": "10.0.0.0/24",
        "gateway": "10.10.1.2",
    },
    {
        "node_name": "r1",
        "destination": "10.0.2.0/24",
        "gateway": "10.10.1.2",
    },
    {
        "node_name": "r1",
        "destination": "10.10.2.0/30",
        "gateway": "10.10.1.2",
    },
    {
        "node_name": "r1",
        "destination": "10.10.3.0/30",
        "gateway": "10.10.1.2",
    },
    {
        "node_name": "r2",
        "destination": "10.0.0.0/24",
        "gateway": "10.10.2.2",
    },
    {
        "node_name": "r2",
        "destination": "10.0.1.0/24",
        "gateway": "10.10.2.2",
    },
    {
        "node_name": "r2",
        "destination": "10.10.1.0/30",
        "gateway": "10.10.2.2",
    },
    {
        "node_name": "r2",
        "destination": "10.10.3.0/30",
        "gateway": "10.10.2.2",
    },
    {
        "node_name": "r_core",
        "destination": "10.0.1.0/24",
        "gateway": "10.10.1.1",
    },
    {
        "node_name": "r_core",
        "destination": "10.0.2.0/24",
        "gateway": "10.10.2.1",
    },
    {
        "node_name": "r_core",
        "destination": "10.0.0.0/24",
        "gateway": "10.10.3.2",
    },
    {
        "node_name": "gw",
        "destination": "10.0.1.0/24",
        "gateway": "10.10.3.1",
    },
    {
        "node_name": "gw",
        "destination": "10.0.2.0/24",
        "gateway": "10.10.3.1",
    },
    {
        "node_name": "gw",
        "destination": "10.10.1.0/30",
        "gateway": "10.10.3.1",
    },
    {
        "node_name": "gw",
        "destination": "10.10.2.0/30",
        "gateway": "10.10.3.1",
    },
)
