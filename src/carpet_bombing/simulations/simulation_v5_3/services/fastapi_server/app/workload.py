"""Charges de travail contrôlées exposées par le service victime."""

from __future__ import annotations

from hashlib import sha256
from time import perf_counter


def light_workload() -> dict[str, object]:
    """Retourne une réponse légère sans travail significatif."""

    return {
        "workload": "light",
        "status": "completed",
    }


def cpu_workload(duration_ms: int) -> dict[str, object]:
    """Occupe le CPU pendant une durée bornée en millisecondes."""

    if not 1 <= duration_ms <= 1000:
        raise ValueError("duration_ms must be between 1 and 1000")

    started_at = perf_counter()
    deadline = started_at + duration_ms / 1000
    iterations = 0
    digest = b"simulation-v5-3"

    while perf_counter() < deadline:
        digest = sha256(digest).digest()
        iterations += 1

    return {
        "workload": "cpu",
        "requested_duration_ms": duration_ms,
        "elapsed_ms": round((perf_counter() - started_at) * 1000, 3),
        "iterations": iterations,
        "checksum_prefix": digest.hex()[:16],
    }
