"""Service responsable du trafic normal et des receivers."""

from __future__ import annotations

from pathlib import Path

from carpet_bombing.simulations.simulation_v5_3.application.ports import (
    ProcessRunner,
)
from carpet_bombing.simulations.simulation_v5_3.domain.simulation_models import (
    SimulationConfig,
)
from carpet_bombing.simulations.simulation_v5_3.domain.topology_models import (
    VictimSpec,
)


class TrafficService:
    """Pilote les processus de trafic normal des victimes."""

    RECEIVER_PROCESS_PATTERN = "packet_receiver.py"
    NORMAL_TRAFFIC_PROCESS_PATTERN = "normal_traffic.py"

    def __init__(
        self,
        config: SimulationConfig,
        process_runner: ProcessRunner,
    ) -> None:
        """Initialise le service avec sa configuration."""
        self._config = config
        self._process_runner = process_runner

    def start(self) -> None:
        """Lance les receivers puis le trafic normal."""
        self.start_receivers()
        self.start_normal_traffic()

    def start_receivers(self) -> None:
        """Lance un receiver TCP/UDP sur chaque victime."""
        for victim in self._config.victims:
            self._process_runner.start(
                victim.name,
                [
                    "python3",
                    str(self._config.scripts.packet_receiver),
                ],
                log_file=Path(
                    f"/tmp/{victim.name}_packet_receiver_v5.log"
                ),
            )

    def start_normal_traffic(self) -> None:
        """Lance un générateur de trafic normal sur chaque victime."""
        for index, victim in enumerate(self._config.victims, start=1):
            self._start_victim_normal_traffic(index, victim)

    def stop(self) -> None:
        """Arrête tous les processus de trafic des victimes."""

        for victim in self._config.victims:
            self._process_runner.stop(
                victim.name,
                self.NORMAL_TRAFFIC_PROCESS_PATTERN,
            )
            self._process_runner.stop(
                victim.name,
                self.RECEIVER_PROCESS_PATTERN,
            )

    def _start_victim_normal_traffic(
        self,
        index: int,
        victim: VictimSpec,
    ) -> None:
        """Lance le trafic normal d'une victime avec ses délais propres."""

        peers = ",".join(
            other_victim.ip_cidr.split("/", maxsplit=1)[0]
            for other_victim in self._config.victims
            if other_victim.name != victim.name
        )

        min_delay = 3 + index % 5
        max_delay = min_delay + 5

        self._process_runner.start(
            victim.name,
            [
                "python3",
                str(self._config.scripts.normal_traffic),
                "--peers",
                peers,
                "--min-delay",
                str(min_delay),
                "--max-delay",
                str(max_delay),
            ],
            log_file=Path(
                f"/tmp/{victim.name}_normal_traffic_v5.log"
            ),
        )
