"""Modèles décrivant les paramètres d'une attaque."""

from dataclasses import dataclass
from typing import Literal


AttackProtocol = Literal["icmp", "udp", "tcp_syn", "dns_amp", "mixed"]
FragmentMode = Literal["manual", "auto", "none"]


@dataclass(frozen=True)
class AttackSettings:
    """Regroupe les paramètres transmis au générateur d'attaque."""

    duration_seconds: int
    packets_per_second: int
    protocol: AttackProtocol
    fragment_mode: FragmentMode

    payload_size: int = 4000
    fragment_size: int = 300
    ttl_min: int = 40
    ttl_max: int = 64
    source_rotation_interval_seconds: float = 5.0

    def __post_init__(self) -> None:
        """Valide les paramètres avant de démarrer l'infrastructure réseau."""

        if self.duration_seconds < 0:
            raise ValueError("Attack duration cannot be negative.")

        if self.packets_per_second <= 0:
            raise ValueError("Packets per second must be greater than zero.")

        if self.payload_size <= 0:
            raise ValueError("Payload size must be greater than zero.")

        if self.fragment_size <= 0:
            raise ValueError("Fragment size must be greater than zero.")

        if self.ttl_min < 1 or self.ttl_max > 255:
            raise ValueError("TTL values must be between 1 and 255.")

        if self.ttl_min > self.ttl_max:
            raise ValueError("Minimum TTL cannot be greater than maximum TTL.")

        if self.source_rotation_interval_seconds <= 0:
            raise ValueError("Source rotation interval must be greater than zero.")
