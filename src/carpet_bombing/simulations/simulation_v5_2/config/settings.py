ATTACKER_COUNT = 4

PARIS_GATEWAY = "10.10.0.254"
CANADA_GATEWAY = "10.20.0.254"

ACTIVE_VICTIM_IPS = [
    "10.20.0.10",
    "10.20.0.11",
    "10.20.0.12",
    "10.20.0.13",
    "10.20.0.14",
    "10.20.0.30",
    "10.20.0.31",
    "10.20.0.32",
    "10.20.0.33",
    "10.20.0.34",
    "10.20.0.50",
    "10.20.0.51",
    "10.20.0.52",
    "10.20.0.53",
    "10.20.0.54",
    "10.20.0.70",
    "10.20.0.71",
    "10.20.0.72",
    "10.20.0.73",
    "10.20.0.74",
]

ATTACK_TARGET_RANGE = "10.20.0.1-10.20.0.80"
SINGLE_TARGET_IP = "10.20.0.10"

SOURCE_RANGES = [
    "10.10.1.1-10.10.1.80",
    "10.10.2.1-10.10.2.80",
    "10.10.3.1-10.10.3.80",
    "10.10.4.1-10.10.4.80",
]

PARIS_TRANSIT_LINK = {
    "paris_ip": "172.16.0.1/30",
    "atlantic_ip": "172.16.0.2/30",
    "atlantic_next_hop": "172.16.0.2",
    "bw": 50,
    "delay": "15ms",
}

ATLANTIC_CANADA_LINK = {
    "atlantic_ip": "172.16.0.5/30",
    "canada_ip": "172.16.0.6/30",
    "canada_next_hop": "172.16.0.6",
    "atlantic_next_hop": "172.16.0.5",
    "bw": 8,
    "delay": "75ms",
    "loss": 0,
}

DEFAULT_DURATION = 45
DEFAULT_ATTACK_DURATION = 30
DEFAULT_WARMUP = 5
DEFAULT_PPS = 200
DEFAULT_PROTOCOL = "mixed"
DEFAULT_FRAGMENT_MODE = "manual"
DEFAULT_FRAGSIZE = 300
DEFAULT_PAYLOAD_SIZE = 4000
DEFAULT_TTL_MIN = 40
DEFAULT_TTL_MAX = 64
DEFAULT_SRC_ROTATION_INTERVAL = 5.0
