from abc import ABC, abstractmethod

from carpet_bombing.mitigation.models import MitigationAction


class MitigationBackend(ABC):
    """Interface implemented by mitigation action backends."""

    @abstractmethod
    def apply(self, action: MitigationAction) -> None:
        """Apply a mitigation action."""
