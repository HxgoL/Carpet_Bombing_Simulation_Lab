"""Fausses implémentations utilisées par les tests V5.3."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence


class FakeCommandRunner:
    """Enregistre les commandes courtes au lieu de les exécuter."""

    def __init__(self) -> None:
        """Initialise la liste des commandes reçues."""

        self.commands: list[tuple[str, tuple[str, ...]]] = []

    def run(self, node_name: str, arguments: Sequence[str]) -> str:
        """Enregistre une commande et retourne une sortie vide."""

        self.commands.append((node_name, tuple(arguments)))
        return ""


class FakeProcessRunner:
    """Enregistre les démarrages et arrêts de processus."""

    def __init__(self) -> None:
        """Initialise les listes d'appels enregistrés."""

        self.started: list[
            tuple[str, tuple[str, ...], Path, int | None]
        ] = []
        self.stopped: list[tuple[str, str]] = []

    def start(
        self,
        node_name: str,
        arguments: Sequence[str],
        *,
        log_file: Path,
        timeout_seconds: int | None = None,
    ) -> None:
        """Enregistre un démarrage de processus."""

        self.started.append(
            (
                node_name,
                tuple(arguments),
                log_file,
                timeout_seconds,
            )
        )

    def stop(self, node_name: str, process_pattern: str) -> None:
        """Enregistre un arrêt de processus."""

        self.stopped.append((node_name, process_pattern))


class FakeClock:
    """Enregistre les attentes sans suspendre réellement les tests."""

    def __init__(self) -> None:
        """Initialise la liste des durées demandées."""

        self.sleeps: list[float] = []

    def sleep(self, seconds: float) -> None:
        """Enregistre la durée demandée."""

        self.sleeps.append(seconds)


class FakeNetwork:
    """Simule le cycle de vie minimal d'un réseau."""

    def __init__(self) -> None:
        """Initialise l'état du réseau."""

        self.start_count = 0
        self.stop_count = 0

    def start(self) -> None:
        """Enregistre le démarrage du réseau."""

        self.start_count += 1

    def stop(self) -> None:
        """Enregistre l'arrêt du réseau."""

        self.stop_count += 1


class FakeInteractiveCli:
    """Simule une CLI interactive sans bloquer les tests."""

    def __init__(self) -> None:
        """Initialise le compteur d'ouvertures."""

        self.run_count = 0

    def run(self) -> None:
        """Enregistre l'ouverture de la CLI."""

        self.run_count += 1