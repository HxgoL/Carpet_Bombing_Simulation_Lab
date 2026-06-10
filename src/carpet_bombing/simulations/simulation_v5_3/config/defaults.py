"""Valeurs par défaut utilisées par la simulation V5.3.

Ce module centralise les constantes de la simulation. Il ne contient aucune
logique Mininet et n'exécute aucune commande.
"""

from __future__ import annotations

from carpet_bombing.simulations.simulation_v5_3.domain.attack_models import (
    AttackProtocol,
    FragmentMode,
)


# Paramètres par défaut des scénarios.
DEFAULT_SCENARIO_DURATION_SECONDS = 45
DEFAULT_ATTACK_DURATION_SECONDS = 30
DEFAULT_WARMUP_SECONDS = 5


# Paramètres par défaut du générateur d'attaque.
DEFAULT_PACKETS_PER_SECOND = 120
DEFAULT_ATTACK_PROTOCOL: AttackProtocol = "mixed"
DEFAULT_FRAGMENT_MODE: FragmentMode = "manual"

DEFAULT_PAYLOAD_SIZE = 4000
DEFAULT_FRAGMENT_SIZE = 300
DEFAULT_TTL_MIN = 40
DEFAULT_TTL_MAX = 64
DEFAULT_SOURCE_ROTATION_INTERVAL_SECONDS = 5.0


# Configuration du réseau des victimes.
VICTIM_GATEWAY = "10.0.0.254"
SINGLE_TARGET_IP = "10.0.0.1"

VICTIM_SWITCH_NAME = "s3"
VICTIM_LINK_BANDWIDTH_MBPS = 5
VICTIM_LINK_DELAY = "10ms"
VICTIM_LINK_LOSS_PERCENT = 0.0


# Configuration des liens entre les routeurs.
ROUTER_LINK_DELAY = "5ms"

