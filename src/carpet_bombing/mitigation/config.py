from dataclasses import dataclass


@dataclass(frozen=True)
class MitigationConfig:
    """Default settings used by mitigation policies."""

    target_prefix: str = "10.0.0.0/24"
    max_packets_per_second: float = 100.0
    max_unique_destinations: int = 10
    dry_run: bool = True
