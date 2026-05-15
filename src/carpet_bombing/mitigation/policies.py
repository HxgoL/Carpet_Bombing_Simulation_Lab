from abc import ABC, abstractmethod

from carpet_bombing.mitigation.config import MitigationConfig
from carpet_bombing.mitigation.models import MitigationAction, MitigationEvent


class MitigationPolicy(ABC):
    """Base class for mitigation decision logic."""

    @abstractmethod
    def decide(self, event: MitigationEvent) -> MitigationAction | None:
        """Return a mitigation action, or None if no action is required."""


class PrefixRateLimitPolicy(MitigationPolicy):
    """Prepare a rate-limit action when prefix-level traffic looks suspicious."""

    def __init__(self, config: MitigationConfig | None = None):
        self.config = config or MitigationConfig()

    def decide(self, event: MitigationEvent) -> MitigationAction | None:
        is_attack = event.label != "normal"
        exceeds_rate = event.packets_per_second >= self.config.max_packets_per_second
        exceeds_fanout = event.unique_dst_count >= self.config.max_unique_destinations

        if not is_attack and not (exceeds_rate and exceeds_fanout):
            return None

        return MitigationAction(
            action_type="prefix_rate_limit",
            target=event.target_prefix,
            reason=(
                "Suspicious prefix-level traffic: "
                f"label={event.label}, "
                f"pps={event.packets_per_second}, "
                f"unique_dst={event.unique_dst_count}"
            ),
            parameters={
                "max_packets_per_second": self.config.max_packets_per_second,
                "dry_run": self.config.dry_run,
            },
        )
