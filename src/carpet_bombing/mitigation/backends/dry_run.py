from carpet_bombing.mitigation.backends.base import MitigationBackend
from carpet_bombing.mitigation.models import MitigationAction


class DryRunBackend(MitigationBackend):
    """Backend that records the last action without changing the system."""

    def __init__(self):
        self.applied_actions: list[MitigationAction] = []

    def apply(self, action: MitigationAction) -> None:
        self.applied_actions.append(action)
