from carpet_bombing.mitigation.backends.base import MitigationBackend
from carpet_bombing.mitigation.backends.dry_run import DryRunBackend
from carpet_bombing.mitigation.models import MitigationAction, MitigationEvent
from carpet_bombing.mitigation.policies import MitigationPolicy, PrefixRateLimitPolicy


class MitigationController:
    """Coordinate mitigation decisions and action application."""

    def __init__(
        self,
        policy: MitigationPolicy | None = None,
        backend: MitigationBackend | None = None,
    ):
        self.policy = policy or PrefixRateLimitPolicy()
        self.backend = backend or DryRunBackend()

    def handle_event(self, event: MitigationEvent) -> MitigationAction | None:
        action = self.policy.decide(event)
        if action is None:
            return None

        self.backend.apply(action)
        return action
