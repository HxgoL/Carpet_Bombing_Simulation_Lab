from __future__ import annotations

import argparse
import ipaddress
import random
import time
from pathlib import Path
from typing import Any

import requests
import yaml
from scapy.all import ICMP, IP, TCP, UDP, Raw, send

#Lecture d'un fichier de configuration YAML pour générer du trafic réseau
def load_config(path:str | None) -> dict[str, Any]:
    if not path:
        return {}
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
    

#transforme string en liste ip
def parse_targets(value: str) -> list[str]:
    