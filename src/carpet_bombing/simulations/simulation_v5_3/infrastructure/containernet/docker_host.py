"""Conversion des modèles métier en paramètres Containernet ``addDocker``."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    VictimSpec,
)


def build_add_docker_options(
    victim: VictimSpec,
    *,
    traffic_generator_root: Path,
) -> dict[str, Any]:
    """Construit les options techniques nécessaires à ``addDocker``.

    Le dossier des générateurs de trafic est monté au même chemin absolu dans
    le conteneur. Les services applicatifs peuvent ainsi utiliser les mêmes
    chemins de scripts avec Mininet et Containernet.
    """

    if victim.container is None:
        raise ValueError(
            f"Victim {victim.name!r} has no container specification."
        )

    options: dict[str, Any] = {
        "dimage": victim.container.image,
        "environment": dict(victim.container.environment),
        "volumes": [
            _read_only_volume(
                traffic_generator_root.resolve(),
                traffic_generator_root.resolve(),
            )
        ],
        # Scapy utilise des sockets brutes pour produire le trafic normal.
        "cap_add": ["NET_RAW"],
    }

    if victim.service is not None:
        options["dcmd"] = shlex.join(victim.service.start_command)

    return options


def _read_only_volume(host_path: Path, container_path: Path) -> str:
    """Décrit un montage Docker en lecture seule."""

    if not host_path.is_dir():
        raise ValueError(
            f"Traffic generator directory does not exist: {host_path}"
        )

    return f"{host_path}:{container_path}:ro"
