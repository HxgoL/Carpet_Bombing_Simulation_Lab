import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

SCENARIO_COLORS = {
    "Normal": "#2ca02c",
    "Normal + attaque": "#d62728",
}
LABEL_COLORS = {
    "normal": "#2ca02c",
    "carpet_udp": "#d62728",
}
NEUTRAL_BLUE = "#1f77b4"

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate traffic analysis graphs from a dataset CSV."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input dataset CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/figures/v1",
        help="Directory where graph images will be written.",
    )
    return parser.parse_args()

def save_current_figure(output_dir, filename):
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=200)
    plt.close()

def format_kilobytes(value, _position):
    return f"{value / 1024:.0f}"


def load_dataset(input_path):
    dataset = pd.read_csv(input_path)
    dataset["relative_window_start"] = dataset.groupby("pcap_file")[
        "window_start"
    ].transform(lambda values: values - values.min())
    dataset["scenario"] = dataset["pcap_file"].apply(scenario_name)
    return dataset

def scenario_name(pcap_file):
    name = pcap_file.lower()
    if "carpet" in name or "attack" in name:
        return "Normal + attaque"
    if "normal" in name:
        return "Normal"
    return pcap_file

def plot_packets_per_second(dataset, output_dir):
    plt.figure(figsize=(10, 5))
    for scenario, group in dataset.groupby("scenario"):
        timeline = group.groupby("relative_window_start")[
            "packets_per_second"
        ].sum().sort_index()
        color = SCENARIO_COLORS.get(scenario)
        plt.fill_between(timeline.index, timeline.values, alpha=0.18, color=color)
        plt.plot(
            timeline.index,
            timeline.values,
            marker="o",
            linewidth=2,
            label=scenario,
            color=color,
        )

    plt.xlabel("Temps depuis le debut de la capture (s)")
    plt.ylabel("Paquets/s")
    plt.title("Evolution du debit de paquets par scenario")
    plt.legend()
    plt.grid(True, alpha=0.3)
    save_current_figure(output_dir, "01_packets_per_second_timeline.png")

def plot_unique_destinations_by_source(dataset, output_dir):
    source_scores = (
        dataset.groupby("src_ip")["unique_dst_count_for_src"]
        .max()
        .sort_values(ascending=False)
        .index
    )
    filtered = dataset[dataset["src_ip"].isin(source_scores)]
    pivot = (
        filtered.groupby(["src_ip", "label"])["unique_dst_count_for_src"]
        .max()
        .unstack(fill_value=0)
        .loc[source_scores]
    )

    colors = [LABEL_COLORS.get(label, "#7f7f7f") for label in pivot.columns]
    pivot.plot(kind="bar", figsize=(10, 5), color=colors)
    plt.xlabel("IP source")
    plt.ylabel("Nombre max de destinations uniques")
    plt.title("Nombre de destinations uniques par source")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title=None)
    plt.grid(True, axis="y", alpha=0.3)
    save_current_figure(output_dir, "02_unique_destinations_by_source.png")

def plot_protocol_distribution(dataset, output_dir):
    protocol_counts = (
        dataset.groupby(["scenario", "protocol"]).size().unstack(fill_value=0)
    )
    protocol_counts.plot(kind="bar", figsize=(8, 5))
    plt.xlabel("Scenario")
    plt.ylabel("Nombre d'entrées du dataset")
    plt.title("Protocoles observés par scénario")
    plt.xticks(rotation=0)
    plt.legend(title=None)
    plt.grid(True, axis="y", alpha=0.3)
    save_current_figure(output_dir, "03_protocol_distribution.png")

def plot_attack_volume_by_destination(dataset, output_dir):
    attack_data = dataset[dataset["label"] != "normal"]
    if attack_data.empty:
        return

    destination_scores = (
        attack_data.groupby("dst_ip")["byte_count"]
        .sum()
        .sort_values(ascending=False)
        .index
    )
    volume = (
        attack_data[attack_data["dst_ip"].isin(destination_scores)]
        .groupby(["dst_ip", "label"])["byte_count"]
        .sum()
        .unstack(fill_value=0)
        .loc[destination_scores]
    )

    colors = [NEUTRAL_BLUE for _label in volume.columns]
    volume.plot(kind="bar", figsize=(11, 5), color=colors)
    plt.xlabel("IP destination")
    plt.ylabel("Volume reçu (Ko)")
    plt.title("Volume d'attaque reçu par destination")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title=None)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_kilobytes))
    plt.grid(True, axis="y", alpha=0.3)
    save_current_figure(output_dir, "04_attack_volume_by_destination.png")

def main():
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset(input_path)
    plot_packets_per_second(dataset, output_dir)
    plot_unique_destinations_by_source(dataset, output_dir)
    plot_protocol_distribution(dataset, output_dir)
    plot_attack_volume_by_destination(dataset, output_dir)

    print(f"Generated graphs in {output_dir.resolve()}")

if __name__ == "__main__":
    main()
