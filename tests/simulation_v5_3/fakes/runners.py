"""Fakes réutilisables pour tester les services sans Mininet."""

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class CommandCall:
    """Enregistre une commande demandée à un nœud."""

    node_name: str
    arguments: tuple[str, ...]


@dataclass
class FakeCommandRunner:
    """Enregistre les commandes au lieu de les exécuter."""

    calls: list[CommandCall] = field(default_factory=list)
    output: str = ""

    def run(self, node_name: str, arguments: Sequence[str]) -> str:
        """Mémorise l'appel et retourne une sortie configurable."""

        self.calls.append(CommandCall(node_name, tuple(arguments)))
        return self.output
