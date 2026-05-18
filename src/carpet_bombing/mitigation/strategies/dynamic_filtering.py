from carpet_bombing.mitigation.models import (
    MitigationAction,
    MitigationActionType,
    MitigationEvent,
)
from carpet_bombing.mitigation.strategies.base import MitigationStrategy


PROTOCOL_BY_LABEL = {
    "carpet_udp": "udp",
    "carpet_tcp_syn": "tcp_syn",
    "carpet_icmp": "icmp",
}


class DynamicFilteringStrategy(MitigationStrategy):
    """Prepare protocol-specific filtering for clearly identified attacks."""

    def supports(self, event: MitigationEvent) -> bool:
        return event.label in PROTOCOL_BY_LABEL

    def build_action(self, event: MitigationEvent) -> MitigationAction:
        protocol = PROTOCOL_BY_LABEL[event.label]
        rule_preview = self._build_iptables_preview(event.target_prefix, protocol)

        return MitigationAction(
            action_type=MitigationActionType.DYNAMIC_FILTER,
            target=event.target_prefix,
            reason=f"Attack traffic classified as {protocol}",
            parameters={
                "protocol": protocol,
                "backend_candidates": ["iptables", "openflow", "sdn_controller"],
                "iptables_preview": rule_preview,
                "rate_limit": self.config.protocol_rate_limit,
                "dry_run": self.config.dry_run,
            },
        )

    def _build_iptables_preview(self, target_prefix: str, protocol: str) -> str:
        if protocol == "tcp_syn":
            return (
                "iptables -A FORWARD "
                f"-d {target_prefix} -p tcp --syn "
                f"-m limit --limit {self.config.protocol_rate_limit} -j ACCEPT"
            )

        return (
            "iptables -A FORWARD "
            f"-d {target_prefix} -p {protocol} "
            f"-m limit --limit {self.config.protocol_rate_limit} -j ACCEPT"
        )
