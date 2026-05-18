from abc import ABC, abstractmethod

from carpet_bombing.mitigation.config import MitigationConfig
from carpet_bombing.mitigation.models import MitigationAction, MitigationEvent


class MitigationStrategy(ABC):
    """Base class for concrete mitigation strategies."""

    def __init__(self, config: MitigationConfig | None = None):
        self.config = config or MitigationConfig()

    @abstractmethod
    def supports(self, event: MitigationEvent) -> bool:
        """Return True if the strategy can handle this event."""

    @abstractmethod
    def build_action(self, event: MitigationEvent) -> MitigationAction:
        """Build the mitigation action for this event."""
