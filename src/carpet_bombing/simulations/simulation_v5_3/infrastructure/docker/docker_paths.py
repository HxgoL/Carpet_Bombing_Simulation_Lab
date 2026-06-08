"""Chemins des contextes Docker appartenant à la simulation V5.3."""

from __future__ import annotations

from pathlib import Path


SIMULATION_ROOT = Path(__file__).resolve().parents[2]

FASTAPI_DOCKER_CONTEXT = (
    SIMULATION_ROOT
    / "services"
    / "fastapi_server"
)

FASTAPI_DOCKERFILE = FASTAPI_DOCKER_CONTEXT / "Dockerfile"
