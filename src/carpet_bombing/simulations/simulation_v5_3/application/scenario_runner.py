"""Stratégies permettant d'exécuter les scénarios automatiques."""

from __future__ import annotations

from typing import Callable, Protocol

from carpet_bombing.simulations.simulation_v5_3.application.attack_service import (
    AttackService,
)
from carpet_bombing.simulations.simulation_v5_3.application.ports import Clock
from carpet_bombing.simulations.simulation_v5_3.domain.models import (
    ScenarioName,
    SimulationConfig,
)


class Scenario(Protocol):
    """Interface commune à toutes les stratégies de scénario."""

    def run(self) -> None:
        """Exécute le scénario jusqu'à sa fin."""


class NormalScenario:
    """Exécute uniquement le trafic normal pendant la durée demandée."""

    def __init__(self, config: SimulationConfig, clock: Clock) -> None:
        """Initialise le scénario avec sa configuration et son horloge."""

        self._config = config
        self._clock = clock

    def run(self) -> None:
        """Attend pendant toute la durée du scénario."""

        duration = self._config.scenario.duration_seconds

        print(f"Scénario normal automatique pendant {duration} secondes")
        self._clock.sleep(duration)


class TimedAttackScenario:
    """Exécute une attaque après une période de trafic normal."""

    def __init__(
        self,
        config: SimulationConfig,
        clock: Clock,
        attack_name: str,
        launch_attack: Callable[[], None],
        stop_attack: Callable[[], None],
    ) -> None:
        """Initialise une stratégie avec les actions d'attaque nécessaires."""

        self._config = config
        self._clock = clock
        self._attack_name = attack_name
        self._launch_attack = launch_attack
        self._stop_attack = stop_attack

    def run(self) -> None:
        """Attend le warmup, lance l'attaque puis garantit son arrêt."""

        duration = self._config.scenario.duration_seconds
        warmup = self._config.scenario.warmup_seconds

        print(
            f"Scénario {self._attack_name} : "
            f"warmup {warmup}s puis attaque"
        )

        self._clock.sleep(warmup)

        try:
            self._launch_attack()
            self._clock.sleep(max(duration - warmup, 0))
        finally:
            self._stop_attack()


class ScenarioRunner:
    """Sélectionne et exécute la stratégie correspondant au scénario demandé."""

    def __init__(
        self,
        config: SimulationConfig,
        attack_service: AttackService,
        clock: Clock,
    ) -> None:
        """Construit le registre des stratégies disponibles."""

        self._strategies: dict[ScenarioName, Scenario] = {
            "normal": NormalScenario(config, clock),
            "single_target": TimedAttackScenario(
                config=config,
                clock=clock,
                attack_name="DDoS single-target",
                launch_attack=attack_service.launch_single_target,
                stop_attack=attack_service.stop,
            ),
            "carpet": TimedAttackScenario(
                config=config,
                clock=clock,
                attack_name="carpet bombing",
                launch_attack=attack_service.launch_carpet,
                stop_attack=attack_service.stop,
            ),
        }

    def run(self, scenario_name: ScenarioName) -> None:
        """Exécute le scénario demandé."""

        strategy = self._strategies[scenario_name]
        strategy.run()