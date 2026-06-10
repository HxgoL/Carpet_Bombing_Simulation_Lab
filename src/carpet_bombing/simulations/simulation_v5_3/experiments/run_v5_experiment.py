import argparse
import json
import os
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
LABELS_FILE = BASE_DIR / "experiments" / "labels_v5.json"
TOPOLOGY_FILE = BASE_DIR / "topology" / "advanced_tclink_topology.py"
PCAP_DIR = BASE_DIR / "pcaps"
CAPTURE_FILTER = (
    "net 10.0.0.0/24 or net 10.0.1.0/24 "
    "or net 10.0.2.0/24 or net 10.10.0.0/16"
)

def parse_args():
    parser = argparse.ArgumentParser(description="Run a V5.3 capture scenario.")
    parser.add_argument(
        "--backend",
        choices=["mininet", "containernet"],
        default="mininet",
        help="Network backend used to run the topology.",
    )
    parser.add_argument(
        "--scenario",
        choices=["normal", "single_target", "carpet", "all"],
        required=True,
        help="Scenario to capture.",
    )
    parser.add_argument("--duration", type=int)
    parser.add_argument("--attack-duration", type=int)
    parser.add_argument("--warmup", type=int)
    parser.add_argument("--pps", type=int, default=120)
    parser.add_argument("--protocol", choices=["icmp", "udp", "tcp_syn", "dns_amp", "mixed"], default="mixed")
    parser.add_argument("--fragment-mode", choices=["manual", "auto", "none"], default="manual")
    return parser.parse_args()

def load_labels():
    with LABELS_FILE.open("r", encoding="utf-8") as labels_file:
        return json.load(labels_file)

def require_root():
    if os.geteuid() != 0:
        raise SystemExit("Run this script with sudo because Mininet and tcpdump need root privileges.")

def run_command(command):
    return subprocess.Popen(command, cwd=REPO_ROOT)

def wait_process(process):
    return_code = process.wait()
    if return_code != 0:
        raise SystemExit(f"Command failed with exit code {return_code}: {' '.join(process.args)}")

def run_checked(command):
    result = subprocess.run(command, cwd=REPO_ROOT, stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        raise SystemExit(f"Command failed with exit code {result.returncode}: {' '.join(command)}")

def wait_capture(process):
    try:
        return_code = process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        return_code = process.wait()
    if return_code not in (0, 130, -2, -9):
        raise SystemExit(f"Capture failed with exit code {return_code}")

def cleanup_mininet():
    subprocess.run(["mn", "-c"], cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        ["pkill", "-f", "advanced_carpet_bombing_attack.py"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["pkill", "-f", "normal_traffic.py"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["pkill", "-f", "packet_receiver.py"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def validate_pcap(pcap_path):
    run_checked(["tcpdump", "-r", str(pcap_path), "-c", "1"])
    run_checked(["tcpdump", "-r", str(pcap_path)])

def capture_scenario(scenario, labels, args):
    cleanup_mininet()
    PCAP_DIR.mkdir(parents=True, exist_ok=True)
    capture_duration = args.duration or labels["capture_duration_seconds"]
    attack_duration = args.attack_duration or labels["attack_duration_seconds"]
    warmup = (
        0
        if scenario == "normal"
        else args.warmup
        if args.warmup is not None
        else labels["warmup_seconds"]
    )
    pcap_file = labels[f"{scenario}_capture"]["pcap_file"]
    pcap_path = PCAP_DIR / pcap_file
    if pcap_path.exists():
        pcap_path.unlink()

    capture_command = [
        "tcpdump",
        "-i",
        "any",
        "-G",
        str(capture_duration),
        "-W",
        "1",
        "-w",
        str(pcap_path),
        CAPTURE_FILTER,
    ]
    topology_command = [
        "python3",
        str(TOPOLOGY_FILE),
        "--backend",
        args.backend,
        "--auto-scenario",
        scenario,
        "--duration",
        str(capture_duration),
        "--attack-duration",
        str(attack_duration),
        "--warmup",
        str(warmup),
        "--pps",
        str(args.pps),
        "--protocol",
        args.protocol,
        "--fragment-mode",
        args.fragment_mode,
    ]

    print(f"\nCapture V5.3 : {scenario}")
    print(f"  pcap : {pcap_path}")
    capture = run_command(capture_command)
    time.sleep(0.5)

    try:
        topology = run_command(topology_command)
        wait_process(topology)
    finally:
        wait_capture(capture)
    validate_pcap(pcap_path)
    cleanup_mininet()
    print(f"Capture {scenario} terminée")

def main():
    args = parse_args()
    require_root()
    labels = load_labels()
    scenarios = ["normal", "single_target", "carpet"] if args.scenario == "all" else [args.scenario]
    for scenario in scenarios:
        capture_scenario(scenario, labels, args)
    print("\nCaptures V5.3 terminées")

if __name__ == "__main__":
    main()
