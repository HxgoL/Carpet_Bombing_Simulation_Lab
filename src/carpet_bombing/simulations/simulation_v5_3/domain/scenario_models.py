"""Modèles décrivant les scénarios exécutables par la simulation."""

from dataclasses import dataclass
from typing import Literal


ScenarioName = Literal["normal", "single_target", "carpet"]


@dataclass(frozen=True)
class ScenarioSettings:
    """Décrit le scénario sélectionné et ses paramètres temporels."""

    name: ScenarioName | None
    duration_seconds: int
    warmup_seconds: int

    def __post_init__(self) -> None:
        """Valide les durées avant le démarrage de la simulation."""

        if self.duration_seconds < 0:
            raise ValueError("Scenario duration cannot be negative.")

        if self.warmup_seconds < 0:
            raise ValueError("Warmup duration cannot be negative.")

        if (
            self.name in ("single_target", "carpet")
            and self.warmup_seconds > self.duration_seconds
        ):
            raise ValueError("Warmup duration cannot exceed scenario duration.")