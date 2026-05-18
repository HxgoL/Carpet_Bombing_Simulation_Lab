from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


def entropy(series: pd.Series) -> float:
    values = series.dropna()
    if values.empty:
        return 0.0

    counts = values.value_counts()
    probs = counts / counts.sum()
    return float(-(probs * probs.map(math.log2)).sum())


def ratio(series: pd.Series, value: str) -> float:
    if series.empty:
        return 0.0
    return float((series == value).sum() / len(series))


def protocol_distribution(group: pd.DataFrame) -> str:
    counts = group["protocol"].fillna("UNKNOWN").value_counts(normalize=True)
    return ";".join(f"{proto}:{value:.4f}" for proto, value in counts.items())


def tcp_flag_distribution(group: pd.DataFrame) -> str:
    flags = group["tcp_flags"].dropna()
    if flags.empty:
        return ""
    counts = flags.value_counts(normalize=True)
    return ";".join(f"{flag}:{value:.4f}" for flag, value in counts.items())


def burstiness(timestamps: pd.Series) -> float:
    deltas = timestamps.sort_values().diff().dropna()
    if deltas.empty:
        return 0.0

    mean = deltas.mean()
    std = deltas.std(ddof=0)

    if mean == 0:
        return 0.0
    return float(std / mean)


def extract_window_features(group: pd.DataFrame, window_seconds: int) -> dict:
    packet_count = len(group)
    byte_count = group["packet_len"].sum()
    unique_dst = group["ip_dst"].nunique()
    top_dst_ratio = 0.0

    if packet_count:
        top_dst_ratio = float(group["ip_dst"].value_counts().iloc[0] / packet_count)

    syn_packets = group["tcp_flags"].fillna("").str.contains("0x0002|S", regex=True).sum()

    return {
        "window_start": group["window_start"].iloc[0],
        "packets_per_second": packet_count / window_seconds,
        "bytes_per_second": byte_count / window_seconds,
        "unique_src_count": group["ip_src"].nunique(),
        "unique_dst_count": unique_dst,
        "fan_out": unique_dst,
        "src_entropy": entropy(group["ip_src"]),
        "dst_entropy": entropy(group["ip_dst"]),
        "protocol_distribution": protocol_distribution(group),
        "syn_ratio": float(syn_packets / packet_count) if packet_count else 0.0,
        "tcp_flag_distribution": tcp_flag_distribution(group),
        "udp_ratio": ratio(group["protocol"], "UDP"),
        "icmp_ratio": ratio(group["protocol"], "ICMP"),
        "dst_port_entropy": entropy(group["dst_port"]),
        "unique_dst_ports": group["dst_port"].nunique(),
        "packet_size_mean": group["packet_len"].mean(),
        "packet_size_std": group["packet_len"].std(ddof=0),
        "src_dst_pair_count": group[["ip_src", "ip_dst"]].drop_duplicates().shape[0],
        "top_dst_ip_ratio": top_dst_ratio,
        "inter_arrival_time_mean": group["timestamp"].sort_values().diff().mean(),
        "inter_arrival_time_std": group["timestamp"].sort_values().diff().std(ddof=0),
        "burstiness_score": burstiness(group["timestamp"]),
        "fanout_growth_rate": 0.0,
        "prefix_packet_rate": packet_count / window_seconds,
        "prefix_byte_rate": byte_count / window_seconds,
        "per_dst_packet_rate_variance": group["ip_dst"].value_counts().var(ddof=0),
        "docker_network_name": "lab_net",
        "capture_point": "monitor",
        "interface_name": "eth0",
        "container_name": "",
    }


def add_growth_rate(features: pd.DataFrame) -> pd.DataFrame:
    features = features.sort_values("window_start")
    features["fanout_growth_rate"] = features["fan_out"].diff().fillna(0.0)
    return features


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["packet_len"] = pd.to_numeric(df["packet_len"], errors="coerce").fillna(0)
    df["dst_port"] = pd.to_numeric(df["dst_port"], errors="coerce")
    df["protocol"] = df["protocol"].fillna("UNKNOWN").str.upper()

    return df.dropna(subset=["timestamp", "ip_src", "ip_dst"])


def extract(input_path: str, output_path: str, window_seconds: int) -> None:
    df = load_csv(input_path)
    base_ts = df["timestamp"].min()
    df["window_start"] = ((df["timestamp"] - base_ts) // window_seconds) * window_seconds + base_ts

    rows = [
        extract_window_features(group, window_seconds)
        for _, group in df.groupby("window_start", sort=True)
    ]

    features = add_growth_rate(pd.DataFrame(rows))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--window-seconds", type=int, default=1)
    args = parser.parse_args()

    extract(args.input, args.output, args.window_seconds)


if __name__ == "__main__":
    main()