"""Compteurs simples conservés en mémoire par le service victime."""

from __future__ import annotations

from collections import Counter
from threading import Lock
from time import monotonic


START_TIME = monotonic()

_lock = Lock()
_requests_total = 0
_errors_total = 0
_requests_by_path: Counter[str] = Counter()


def record_request(path: str) -> None:
    """Enregistre une requête reçue."""

    global _requests_total

    with _lock:
        _requests_total += 1
        _requests_by_path[path] += 1


def record_error() -> None:
    """Enregistre une erreur de traitement."""

    global _errors_total

    with _lock:
        _errors_total += 1


def metrics_snapshot() -> dict[str, object]:
    """Retourne une copie cohérente des compteurs."""

    with _lock:
        return {
            "uptime_seconds": round(monotonic() - START_TIME, 3),
            "requests_total": _requests_total,
            "errors_total": _errors_total,
            "requests_by_path": dict(_requests_by_path),
        }
