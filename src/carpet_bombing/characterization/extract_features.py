import argparse
import csv
import ipaddress
import math
from collections import defaultdict
from pathlib import Path

from scapy.all import ICMP, IP, TCP, UDP, PcapReader


DEFAULT_COLUMNS = [
    "window_start",
    "window_end",
    "src_ip",
    "dst_ip",
    "protocol",
    "src_port",
    "dst_port",
    "packet_count",
    "byte_count",
    "packets_per_second",
    "bytes_per_second",
    "unique_dst_count_for_src",
    "is_dst_inactive",
    "ttl_min",
    "ttl_max",
    "ttl_mean",
    "ttl_std",
    "unique_ttl_count",
    "fragmented_packet_count",
    "first_fragment_count",
    "non_initial_fragment_count",
    "fragment_ratio",
    "label",
    "pcap_file",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract flow features from pcap files into a shared CSV dataset."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input pcap file or directory containing .pcap/.pcapng files.",
    )
    parser.add_argument("--output", required=True, help="Output CSV file path.")
    parser.add_argument(
        "--window-size",
        type=float,
        default=1.0,
        help="Aggregation window size in seconds.",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="Dataset label. If omitted, the label is inferred from each pcap filename.",
    )
    parser.add_argument(
        "--inactive-ranges",
        default="10.0.0.20-10.0.0.40",
        help="Comma-separated inactive IP ranges, for example 10.0.0.20-10.0.0.40.",
    )
    parser.add_argument(
        "--attack-src-ip",
        default=None,
        help="Source IP used to identify attack flows in mixed captures.",
    )
    parser.add_argument(
        "--attack-targets",
        default=None,
        help="Attack destination IPs or ranges, for example 10.0.0.1-10.0.0.8.",
    )
    parser.add_argument(
        "--attack-protocol",
        choices=["ICMP", "TCP", "UDP"],
        default=None,
        help="Protocol used to identify attack flows in mixed captures.",
    )
    parser.add_argument(
        "--attack-label",
        default="carpet_udp",
        help="Label assigned to flows matching the attack criteria.",
    )
    parser.add_argument(
        "--background-label",
        default="normal",
        help="Label assigned to flows that do not match attack criteria in mixed captures.",
    )
    return parser.parse_args()


def iter_pcap_files(input_path):
    path = Path(input_path)
    if path.is_file():
        return [path]

    return sorted(
        file
        for pattern in ("*.pcap", "*.pcapng")
        for file in path.rglob(pattern)
    )


def parse_inactive_ranges(raw_ranges):
    return parse_ip_ranges(raw_ranges)

def parse_ip_ranges(raw_ranges):
    ips = set()

    if not raw_ranges:
        return ips

    for raw_range in raw_ranges.split(","):
        value = raw_range.strip()
        if not value:
            continue

        if "-" not in value:
            ips.add(str(ipaddress.ip_address(value)))
            continue

        start_raw, end_raw = value.split("-", maxsplit=1)
        start = ipaddress.ip_address(start_raw.strip())
        end = ipaddress.ip_address(end_raw.strip())

        if int(end) < int(start):
            raise ValueError(f"Invalid inactive IP range: {value}")

        for ip_int in range(int(start), int(end) + 1):
            ips.add(str(ipaddress.ip_address(ip_int)))

    return ips


def infer_label(pcap_file):
    name = pcap_file.stem.lower()
    if name.startswith("normal"):
        return "normal"
    if "single" in name:
        return "ddos_single_target"
    if "udp" in name:
        return "carpet_udp"
    if "tcp" in name or "syn" in name:
        return "carpet_tcp_syn"
    if "icmp" in name:
        return "carpet_icmp"
    if "mixed" in name:
        return "carpet_mixed"
    if "attack" in name or "carpet" in name:
        return "attack"
    return "unknown"


def packet_protocol(packet):
    if packet.haslayer(TCP):
        return "TCP", int(packet[TCP].sport), int(packet[TCP].dport)
    if packet.haslayer(UDP):
        return "UDP", int(packet[UDP].sport), int(packet[UDP].dport)
    if packet.haslayer(ICMP):
        return "ICMP", "", ""

    protocol_by_number = {1: "ICMP", 6: "TCP", 17: "UDP"}
    return protocol_by_number.get(int(packet[IP].proto), str(packet[IP].proto)), "", ""


def packet_fragmentation(packet):
    ip_layer = packet[IP]
    more_fragments = bool(int(ip_layer.flags) & 0x1)
    fragment_offset = int(ip_layer.frag)
    is_fragmented = more_fragments or fragment_offset > 0

    return {
        "is_fragmented": is_fragmented,
        "is_first_fragment": more_fragments and fragment_offset == 0,
        "is_non_initial_fragment": fragment_offset > 0,
    }


def is_attack_flow(src_ip, dst_ip, protocol, attack_config):
    if not attack_config:
        return False

    if attack_config["src_ip"] and src_ip != attack_config["src_ip"]:
        return False

    if attack_config["protocol"] and protocol != attack_config["protocol"]:
        return False

    if attack_config["targets"] and dst_ip not in attack_config["targets"]:
        return False

    return True


def resolve_flow_label(default_label, src_ip, dst_ip, protocol, attack_config):
    if not attack_config:
        return default_label

    if is_attack_flow(src_ip, dst_ip, protocol, attack_config):
        return attack_config["attack_label"]

    return attack_config["background_label"]


def extract_pcap_features(pcap_file, window_size, label, inactive_ips, attack_config):
    flows = defaultdict(
        lambda: {
            "packet_count": 0,
            "byte_count": 0,
            "ttl_sum": 0,
            "ttl_squared_sum": 0,
            "ttl_values": set(),
            "fragmented_packet_count": 0,
            "first_fragment_count": 0,
            "non_initial_fragment_count": 0,
        }
    )
    src_window_destinations = defaultdict(set)

    with PcapReader(str(pcap_file)) as packets:
        for packet in packets:
            if not packet.haslayer(IP):
                continue

            timestamp = float(packet.time)
            window_start = timestamp - (timestamp % window_size)
            window_end = window_start + window_size
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            protocol, src_port, dst_port = packet_protocol(packet)
            ttl = int(packet[IP].ttl)
            fragmentation = packet_fragmentation(packet)
            flow_label = resolve_flow_label(
                default_label=label,
                src_ip=src_ip,
                dst_ip=dst_ip,
                protocol=protocol,
                attack_config=attack_config,
            )

            flow_key = (
                window_start,
                window_end,
                src_ip,
                dst_ip,
                protocol,
                src_port,
                dst_port,
                flow_label,
            )

            flows[flow_key]["packet_count"] += 1
            flows[flow_key]["byte_count"] += len(packet)
            flows[flow_key]["ttl_sum"] += ttl
            flows[flow_key]["ttl_squared_sum"] += ttl * ttl
            flows[flow_key]["ttl_values"].add(ttl)
            flows[flow_key]["fragmented_packet_count"] += int(
                fragmentation["is_fragmented"]
            )
            flows[flow_key]["first_fragment_count"] += int(
                fragmentation["is_first_fragment"]
            )
            flows[flow_key]["non_initial_fragment_count"] += int(
                fragmentation["is_non_initial_fragment"]
            )
            src_window_destinations[(window_start, src_ip)].add(dst_ip)

    rows = []
    for flow_key, counters in sorted(
        flows.items(),
        key=lambda item: tuple(str(value) for value in item[0]),
    ):
        (
            window_start,
            window_end,
            src_ip,
            dst_ip,
            protocol,
            src_port,
            dst_port,
            flow_label,
        ) = flow_key

        packet_count = counters["packet_count"]
        byte_count = counters["byte_count"]
        ttl_mean = counters["ttl_sum"] / packet_count
        ttl_variance = max(
            counters["ttl_squared_sum"] / packet_count - ttl_mean * ttl_mean,
            0.0,
        )
        rows.append(
            {
                "window_start": f"{window_start:.6f}",
                "window_end": f"{window_end:.6f}",
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "protocol": protocol,
                "src_port": src_port,
                "dst_port": dst_port,
                "packet_count": packet_count,
                "byte_count": byte_count,
                "packets_per_second": packet_count / window_size,
                "bytes_per_second": byte_count / window_size,
                "unique_dst_count_for_src": len(
                    src_window_destinations[(window_start, src_ip)]
                ),
                "is_dst_inactive": int(dst_ip in inactive_ips),
                "ttl_min": min(counters["ttl_values"]),
                "ttl_max": max(counters["ttl_values"]),
                "ttl_mean": ttl_mean,
                "ttl_std": math.sqrt(ttl_variance),
                "unique_ttl_count": len(counters["ttl_values"]),
                "fragmented_packet_count": counters["fragmented_packet_count"],
                "first_fragment_count": counters["first_fragment_count"],
                "non_initial_fragment_count": counters[
                    "non_initial_fragment_count"
                ],
                "fragment_ratio": counters["fragmented_packet_count"]
                / packet_count,
                "label": flow_label,
                "pcap_file": pcap_file.name,
            }
        )

    return rows


def write_dataset(rows, output_path):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=DEFAULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    pcap_files = iter_pcap_files(args.input)
    inactive_ips = parse_inactive_ranges(args.inactive_ranges)
    attack_targets = parse_ip_ranges(args.attack_targets)
    attack_config = None

    if args.attack_src_ip or args.attack_protocol or attack_targets:
        attack_config = {
            "src_ip": args.attack_src_ip,
            "targets": attack_targets,
            "protocol": args.attack_protocol,
            "attack_label": args.attack_label,
            "background_label": args.background_label,
        }

    if not pcap_files:
        raise FileNotFoundError(f"No pcap files found in {args.input}")

    rows = []
    for pcap_file in pcap_files:
        label = args.label or infer_label(pcap_file)
        rows.extend(
            extract_pcap_features(
                pcap_file=pcap_file,
                window_size=args.window_size,
                label=label,
                inactive_ips=inactive_ips,
                attack_config=attack_config,
            )
        )

    write_dataset(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
