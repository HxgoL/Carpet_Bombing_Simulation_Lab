# Carpet Bombing Simulation Lab

Experimental platform for detecting, characterizing and mitigating carpet bombing DDoS attacks.

## Project Structure

```text
src/
├── detection/
├── characterization/
├── mitigation/
└── traffic_generator/
```

## Requirements

- Python 3.12
- Poetry
- Linux / WSL recommended for Mininet and network tools

## Installation

Clone the repository:

```bash
git clone <repo-url>
cd Carpet_Bombing_Simulation_Lab
```

Install dependencies:

```bash
poetry install
```

Activate virtual environment:

```bash
poetry shell
```

## Main Dependencies

- scapy
- pandas
- numpy
- matplotlib
- scikit-learn
- pyshark
- jupyter

## Network Tools

System tools required:

```bash
sudo apt install mininet tshark tcpdump wireshark iperf3
```

## Objectives

- Generate legitimate and malicious traffic
- Simulate carpet bombing attacks
- Extract network features
- Detect anomalies
- Apply mitigation strategies
- Evaluate detection and mitigation performance

## Team Roles

- Hugo → Detection / architecture
- Eve → Characterization / threat intelligence
- Doha → Mitigation

## Notes

Large `.pcap` files and generated datasets are ignored via `.gitignore`.