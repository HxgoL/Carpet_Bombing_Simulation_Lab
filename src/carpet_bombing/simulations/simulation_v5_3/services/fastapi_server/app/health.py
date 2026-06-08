"""Réponse de healthcheck du service victime."""

from __future__ import annotations

from time import monotonic


START_TIME = monotonic()


def health_payload() -> dict[str, object]:
    """Retourne un état simple et l'uptime du service."""

    return {
        "status": "ok",
        "uptime_seconds": round(monotonic() - START_TIME, 3),
    }
