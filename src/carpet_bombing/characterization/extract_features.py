import argparse
import csv
import ipaddress
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
    inactive_ips = set()

    for raw_range in raw_ranges.split(","):
        value = raw_range.strip()
        if not value:
            continue

        if "-" not in value:
            inactive_ips.add(str(ipaddress.ip_address(value)))
            continue

        start_raw, end_raw = value.split("-", maxsplit=1)
        start = ipaddress.ip_address(start_raw.strip())
        end = ipaddress.ip_address(end_raw.strip())

        if int(end) < int(start):
            raise ValueError(f"Invalid inactive IP range: {value}")

        for ip_int in range(int(start), int(end) + 1):
            inactive_ips.add(str(ipaddress.ip_address(ip_int)))

    return inactive_ips


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
    return str(packet[IP].proto), "", ""


def extract_pcap_features(pcap_file, window_size, label, inactive_ips):
    flows = defaultdict(lambda: {"packet_count": 0, "byte_count": 0})
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

            flow_key = (
                window_start,
                window_end,
                src_ip,
                dst_ip,
                protocol,
                src_port,
                dst_port,
            )

            flows[flow_key]["packet_count"] += 1
            flows[flow_key]["byte_count"] += len(packet)
            src_window_destinations[(window_start, src_ip)].add(dst_ip)

    rows = []
    for flow_key, counters in sorted(flows.items()):
        (
            window_start,
            window_end,
            src_ip,
            dst_ip,
            protocol,
            src_port,
            dst_port,
        ) = flow_key

        packet_count = counters["packet_count"]
        byte_count = counters["byte_count"]
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
                "label": label,
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
            )
        )

    write_dataset(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
