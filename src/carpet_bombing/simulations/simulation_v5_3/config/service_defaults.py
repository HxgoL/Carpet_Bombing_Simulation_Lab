"""Valeurs par défaut du service HTTP exécuté par les victimes Docker."""

from __future__ import annotations


FASTAPI_SERVICE_NAME = "victim-fastapi"

FASTAPI_IMAGE = "carpet-bombing-fastapi-v5-3:latest"

FASTAPI_INTERNAL_PORT = 8000

FASTAPI_HEALTHCHECK_PATH = "/health"

FASTAPI_START_COMMAND = (
    "uvicorn",
    "app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    str(FASTAPI_INTERNAL_PORT),
)

FASTAPI_ENVIRONMENT = (
    ("PYTHONUNBUFFERED", "1"),
)