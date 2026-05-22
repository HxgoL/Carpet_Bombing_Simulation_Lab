import argparse
from pathlib import Path
from math import log2
import matplotlib.pyplot as plt
import pandas as pd

ATTACK_LABEL = "carpet_udp"
SCENARIOS = ["Normal", "Normal + attaque"]
TARGET_DESTINATIONS = [f"10.0.0.{i}" for i in range(1, 41)]
COLORS = {
    "Actives": "#1f77b4",
    "Inactives": "#ff7f0e",
    "Normal": "#2ca02c",
    "Normal + attaque": "#d62728",
}

def parse_args():
    parser = argparse.ArgumentParser(description="Generate V3 characterization graphs.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default="docs/figures/v3")
    return parser.parse_args()

def save_current_figure(output_dir, filename):
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=200)
    plt.close()

def scenario_name(pcap_file):
    name = pcap_file.lower()
    if "normal" in name:
        return "Normal"
    if "attack" in name or "carpet" in name:
        return "Normal + attaque"
    return "Normal"

def load_dataset(input_path):
    dataset = pd.read_csv(input_path)
    dataset["relative_window_start"] = dataset.groupby("pcap_file")[
        "window_start"
    ].transform(lambda values: values - values.min())
    dataset["scenario"] = dataset["pcap_file"].apply(scenario_name)
    dataset["destination_type"] = dataset["is_dst_inactive"].map(
        {0: "Actives", 1: "Inactives"}
    )
    return dataset

def plot_packets_per_second(dataset, output_dir):
    plt.figure(figsize=(10, 5))
    for scenario in SCENARIOS:
        group = dataset[dataset["scenario"] == scenario]
        if group.empty:
            continue
        timeline = group.groupby("relative_window_start")[
            "packets_per_second"
        ].sum().sort_index()
        color = COLORS[scenario]
        plt.fill_between(timeline.index, timeline.values, alpha=0.18, color=color)
        plt.plot(timeline.index, timeline.values, marker="o", linewidth=2, label=scenario, color=color)
    plt.yscale("log")
    plt.xlabel("Temps depuis le début de la capture (s)")
    plt.ylabel("Paquets/s")
    plt.title("Évolution du débit de paquets par scénario")
    plt.legend()
    plt.grid(True, alpha=0.3)
    save_current_figure(output_dir, "01_packets_per_second_timeline.png")

def plot_active_inactive_destinations(dataset, output_dir):
    attack_data = dataset[dataset["label"] == ATTACK_LABEL]
    unique_destinations = (
        attack_data.groupby(["src_ip", "destination_type"])["dst_ip"]
        .nunique()
        .unstack(fill_value=0)
        .sort_index()
    )
    unique_destinations = unique_destinations.reindex(
        columns=["Actives", "Inactives"], fill_value=0
    )
    unique_destinations.plot(
        kind="bar",
        stacked=True,
        figsize=(9, 5),
        color=[COLORS["Actives"], COLORS["Inactives"]],
    )
    plt.xlabel("IP attaquante")
    plt.ylabel("Nombre de destinations uniques")
    plt.title("Destinations actives et inactives ciblées par attaquant")
    plt.xticks(rotation=0)
    plt.legend(title=None)
    plt.grid(True, axis="y", alpha=0.3)
    save_current_figure(output_dir, "02_active_inactive_destinations_by_attacker.png")

def plot_protocol_distribution(dataset, output_dir):
    protocol_counts = (
        dataset.groupby(["scenario", "protocol"]).size().unstack(fill_value=0)
    )
    protocol_counts = protocol_counts.reindex(SCENARIOS, fill_value=0)
    protocol_counts.plot(kind="bar", figsize=(8, 5))
    plt.xlabel("Scénario")
    plt.ylabel("Nombre d'entrées du dataset")
    plt.title("Protocoles observés par scénario")
    plt.xticks(rotation=0)
    plt.yscale("log")
    plt.legend(title=None)
    plt.grid(True, axis="y", alpha=0.3)
    save_current_figure(output_dir, "03_protocol_distribution.png")

def entropy(values):
    total = values.sum()
    if total == 0:
        return 0
    probabilities = values / total
    return -sum(probability * log2(probability) for probability in probabilities if probability > 0)

def plot_destination_fanout_timeline(dataset, output_dir):
    attack_data = dataset[dataset["label"] == ATTACK_LABEL]
    timeline = (
        attack_data.groupby("relative_window_start")["dst_ip"]
        .nunique()
        .sort_index()
    )

    plt.figure(figsize=(10, 5))
    plt.fill_between(timeline.index, timeline.values, alpha=0.18, color=COLORS["Inactives"])
    plt.plot(timeline.index, timeline.values, marker="o", linewidth=2, color=COLORS["Inactives"])
    plt.xlabel("Temps depuis le début de la capture (s)")
    plt.ylabel("Destinations uniques")
    plt.title("Fan-out de l'attaque dans le temps")
    plt.grid(True, alpha=0.3)
    save_current_figure(output_dir, "04_destination_fanout_timeline.png")

def plot_attack_source_destination_map(dataset, output_dir):
    attack_data = dataset[dataset["label"] == ATTACK_LABEL]
    source_order = sorted(attack_data["src_ip"].unique())
    heatmap = (
        attack_data.groupby(["src_ip", "dst_ip"])["packet_count"]
        .sum()
        .unstack(fill_value=0)
        .reindex(index=source_order, columns=TARGET_DESTINATIONS, fill_value=0)
    )

    plt.figure(figsize=(13, 4.5))
    image = plt.imshow(heatmap, aspect="auto", cmap="YlOrRd")
    plt.colorbar(image, label="Paquets")
    plt.xlabel("IP destination")
    plt.ylabel("IP attaquante")
    plt.title("Carte source-destination de l'attaque")
    plt.xticks(range(len(TARGET_DESTINATIONS)), TARGET_DESTINATIONS, rotation=90, fontsize=7)
    plt.yticks(range(len(source_order)), source_order)
    plt.axvline(7.5, color="#333333", linestyle="--", linewidth=1)
    save_current_figure(output_dir, "05_attack_source_destination_map.png")

def plot_destination_entropy_timeline(dataset, output_dir):
    entropy_by_scenario = {}
    for scenario in SCENARIOS:
        scenario_data = dataset[dataset["scenario"] == scenario]
        entropy_by_scenario[scenario] = (
            scenario_data.groupby("relative_window_start")[["dst_ip", "packet_count"]]
            .apply(lambda group: entropy(group.groupby("dst_ip")["packet_count"].sum()))
            .sort_index()
        )

    plt.figure(figsize=(10, 5))
    for scenario, timeline in entropy_by_scenario.items():
        color = COLORS[scenario]
        plt.plot(timeline.index, timeline.values, marker="o", linewidth=2, label=scenario, color=color)
    plt.xlabel("Temps depuis le début de la capture (s)")
    plt.ylabel("Entropie des destinations")
    plt.title("Dispersion du trafic vers les destinations")
    plt.legend()
    plt.grid(True, alpha=0.3)
    save_current_figure(output_dir, "06_destination_entropy_timeline.png")

def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset(args.input)
    plot_packets_per_second(dataset, output_dir)
    plot_active_inactive_destinations(dataset, output_dir)
    plot_protocol_distribution(dataset, output_dir)
    plot_destination_fanout_timeline(dataset, output_dir)
    plot_attack_source_destination_map(dataset, output_dir)
    plot_destination_entropy_timeline(dataset, output_dir)
    print(f"Generated graphs in {output_dir.resolve()}")

if __name__ == "__main__":
    main()
