from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MitigationActionType(StrEnum):
    """Supported mitigation action families."""

    DYNAMIC_FILTER = "dynamic_filter"
    PREFIX_RATE_LIMIT = "prefix_rate_limit"
    TRAFFIC_CLASSIFICATION = "traffic_classification"
    TRAFFIC_REDISTRIBUTION = "traffic_redistribution"
    EMERGENCY_BLOCK = "emergency_block"


@dataclass(frozen=True)
class MitigationEvent:
    """Detection result consumed by the mitigation module."""

    label: str
    target_prefix: str
    packets_per_second: float
    unique_dst_count: int
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MitigationAction:
    """Action prepared by a mitigation policy."""

    action_type: MitigationActionType
    target: str
    reason: str
    parameters: dict[str, Any] = field(default_factory=dict)
