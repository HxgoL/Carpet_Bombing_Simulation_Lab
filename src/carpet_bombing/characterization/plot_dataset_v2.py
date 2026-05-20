import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

LINK_LIMIT_MBPS = 5
PLOT_DURATION = 30
COLORS = {"Normal": "#2ca02c", "Normal + attaque": "#d62728"}


def scenario_name(pcap_file):
    name = pcap_file.lower()
    if "carpet" in name or "attack" in name:
        return "Normal + attaque"
    return "Normal"


def main():
    parser = argparse.ArgumentParser(description="Generate the V2 TCLink graph.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default="docs/figures/v2")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = pd.read_csv(args.input)
    dataset["relative_window_start"] = dataset.groupby("pcap_file")[
        "window_start"
    ].transform(lambda values: values - values.min())
    dataset = dataset[dataset["relative_window_start"] <= PLOT_DURATION].copy()
    dataset["scenario"] = dataset["pcap_file"].apply(scenario_name)
    dataset["mbits_per_second"] = dataset["bytes_per_second"] * 8 / 1_000_000

    plt.figure(figsize=(10, 5))
    max_bandwidth = 0
    for scenario, group in dataset.groupby("scenario"):
        timeline = group.groupby("relative_window_start")["mbits_per_second"].sum()
        max_bandwidth = max(max_bandwidth, timeline.max())
        color = COLORS[scenario]
        plt.fill_between(timeline.index, timeline.values, alpha=0.18, color=color)
        plt.plot(timeline.index, timeline.values, marker="o", linewidth=2, label=scenario, color=color)

    plt.axhline(
        LINK_LIMIT_MBPS,
        color="#333333",
        linestyle="--",
        linewidth=1.5,
        label=f"Limite TCLink ({LINK_LIMIT_MBPS} Mbit/s)",
    )
    plt.yscale("log")
    plt.xlim(0, PLOT_DURATION)
    plt.ylim(0.0005, max_bandwidth * 1.6)
    plt.xlabel("Temps depuis le debut de la capture (s)")
    plt.ylabel("Mbit/s")
    plt.title("Débit observé face à la limite TCLink")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "01_tclink_bandwidth_timeline.png", dpi=200)
    plt.close()

    print(f"Generated graph in {output_dir.resolve()}")


if __name__ == "__main__":
    main()
