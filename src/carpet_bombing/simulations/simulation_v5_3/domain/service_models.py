"""Modèles métier décrivant les conteneurs et services applicatifs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContainerSpec:
    """Décrit les besoins génériques d'un hôte conteneurisé.

    Le domaine connaît l'idée d'un conteneur, mais ne connaît ni Docker,
    ni Containernet, ni la méthode technique utilisée pour le créer.
    """

    image: str
    environment: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        """Valide les propriétés génériques du conteneur."""

        if not self.image.strip():
            raise ValueError("Container image cannot be empty.")

        environment_names = [
            variable_name
            for variable_name, _value in self.environment
        ]

        if len(environment_names) != len(set(environment_names)):
            raise ValueError(
                "Container environment variable names must be unique."
            )


@dataclass(frozen=True)
class ServiceSpec:
    """Décrit un service réseau exécuté par un hôte.

    Cette classe ne connaît pas FastAPI. Elle représente simplement un service
    possédant un port, une commande de démarrage et un healthcheck.
    """

    name: str
    internal_port: int
    start_command: tuple[str, ...]
    healthcheck_path: str

    def __post_init__(self) -> None:
        """Valide les propriétés du service."""

        if not self.name.strip():
            raise ValueError("Service name cannot be empty.")

        if not 1 <= self.internal_port <= 65535:
            raise ValueError("Service port must be between 1 and 65535.")

        if not self.start_command:
            raise ValueError("Service start command cannot be empty.")

        if not self.healthcheck_path.startswith("/"):
            raise ValueError("Healthcheck path must start with '/'.")