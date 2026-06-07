"""Service applicatif responsable des attaques simulées."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from carpet_bombing.simulations.simulation_v5_3.application.ports import (
    ProcessRunner,
)
from carpet_bombing.simulations.simulation_v5_3.domain.simulation_models import (
    SimulationConfig,
)


DestinationArgument = tuple[str, str]


class AttackService:
    """Lance et arrête les scénarios d'attaque sur les attaquants."""

    ATTACK_PROCESS_PATTERN = "advanced_carpet_bombing_attack.py"

    def __init__(
        self,
        config: SimulationConfig,
        process_runner: ProcessRunner,
    ) -> None:
        """Initialise le service avec sa configuration."""

        self._config = config
        self._process_runner = process_runner

    def launch_single_target(self) -> None:
        """Lance une attaque concentrée sur une seule victime."""

        destinations = [
            ("--dst-ip", self._config.single_target_ip)
            for _attacker in self._config.attackers
        ]

        self._launch("single_target", destinations)

    def launch_carpet(self) -> None:
        """Lance une attaque distribuée sur plusieurs plages de victimes."""

        destinations = [
            ("--dst-range", attacker.carpet_target_range)
            for attacker in self._config.attackers
        ]

        self._launch("carpet", destinations)

    def stop(self) -> None:
        """Arrête les processus d'attaque sur tous les attaquants."""

        for attacker in self._config.attackers:
            self._process_runner.stop(
                attacker.name,
                self.ATTACK_PROCESS_PATTERN,
            )

    def _launch(
        self,
        attack_name: str,
        destinations: Sequence[DestinationArgument],
    ) -> None:
        """Lance une commande d'attaque adaptée à chaque attaquant."""

        attack = self._config.attack

        for attacker, destination in zip(
            self._config.attackers,
            destinations,
            strict=True,
        ):
            destination_flag, destination_value = destination

            arguments = [
                "python3",
                str(self._config.scripts.attack_generator),
                destination_flag,
                destination_value,
                "--src-range",
                attacker.simulated_source_range,
                "--duration",
                str(attack.duration_seconds),
                "--pps",
                str(attack.packets_per_second),
                "--protocol",
                attack.protocol,
                "--payload-size",
                str(attack.payload_size),
                "--fragment-mode",
                attack.fragment_mode,
                "--fragsize",
                str(attack.fragment_size),
                "--ttl-min",
                str(attack.ttl_min),
                "--ttl-max",
                str(attack.ttl_max),
                "--src-rotation-interval",
                str(attack.source_rotation_interval_seconds),
            ]

            self._process_runner.start(
                attacker.name,
                arguments,
                timeout_seconds=attack.duration_seconds,
                log_file=Path(
                    f"/tmp/{attacker.name}_{attack_name}_attack_v5_3.log"
                ),
            )
