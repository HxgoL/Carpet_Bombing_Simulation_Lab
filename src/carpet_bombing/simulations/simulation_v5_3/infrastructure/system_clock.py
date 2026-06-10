"""Implémentation réelle de l'horloge utilisée par les scénarios."""

from __future__ import annotations

import time


class SystemClock:
    """Horloge utilisant le temps réel du système."""

    def sleep(self, seconds: float) -> None:
        """Suspend l'exécution pendant la durée demandée."""
        time.sleep(seconds)
