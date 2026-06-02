from pathlib import Path


TRAFFIC_DIR = Path(__file__).resolve().parents[1] / "traffic"
NORMAL_SCRIPT = TRAFFIC_DIR / "normal_traffic.py"
RECEIVER_SCRIPT = TRAFFIC_DIR / "packet_receiver.py"


def start_receivers(victims):
    for victim in victims:
        victim.cmd(f"python3 {RECEIVER_SCRIPT} > /tmp/{victim.name}_packet_receiver_v5.log 2>&1 &")


def start_normal_traffic(victims):
    for index, victim in enumerate(victims, start=1):
        peers = ",".join(v.IP() for v in victims if v != victim)
        min_delay = 4 + index % 4
        max_delay = min_delay + 6
        victim.cmd(
            f"python3 {NORMAL_SCRIPT} --peers {peers} "
            f"--min-delay {min_delay} --max-delay {max_delay} "
            f"> /tmp/{victim.name}_normal_traffic_v5.log 2>&1 &"
        )
