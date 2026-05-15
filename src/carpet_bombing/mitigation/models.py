from dataclasses import dataclass, field
from typing import Any


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

    action_type: str
    target: str
    reason: str
    parameters: dict[str, Any] = field(default_factory=dict)
