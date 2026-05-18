from abc import ABC, abstractmethod

from carpet_bombing.mitigation.config import MitigationConfig
from carpet_bombing.mitigation.models import MitigationAction, MitigationEvent
from carpet_bombing.mitigation.strategies.dynamic_filtering import (
    DynamicFilteringStrategy,
)


class MitigationPolicy(ABC):
    """Base class for mitigation decision logic."""

    @abstractmethod
    def decide(self, event: MitigationEvent) -> MitigationAction | None:
        """Return a mitigation action, or None if no action is required."""


class AdaptiveMitigationPolicy(MitigationPolicy):
    """Choose the available mitigation strategy for the current event."""

    def __init__(self, config: MitigationConfig | None = None):
        self.config = config or MitigationConfig()
        self.dynamic_filtering = DynamicFilteringStrategy(self.config)

    def decide(self, event: MitigationEvent) -> MitigationAction | None:
        if event.label == "normal":
            return None

        if self.dynamic_filtering.supports(event):
            return self.dynamic_filtering.build_action(event)

        return None
