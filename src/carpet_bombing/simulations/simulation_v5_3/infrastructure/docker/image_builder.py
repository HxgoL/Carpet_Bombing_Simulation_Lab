"""Helper minimal construisant une image avec la commande Docker."""

from __future__ import annotations

import subprocess
from pathlib import Path


def ensure_image(image: str, context: Path) -> None:
    """Construit l'image uniquement lorsqu'elle n'existe pas localement."""

    if image_exists(image):
        return

    build_image(image, context)


def image_exists(image: str) -> bool:
    """Indique si une image Docker existe localement."""

    try:
        result = subprocess.run(
            ["docker", "image", "inspect", image],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "Docker CLI is required for the Containernet backend."
        ) from error

    return result.returncode == 0


def build_image(image: str, context: Path) -> None:
    """Construit une image Docker depuis le contexte fourni."""

    if not context.is_dir():
        raise ValueError(f"Docker context does not exist: {context}")

    dockerfile = context / "Dockerfile"

    if not dockerfile.is_file():
        raise ValueError(f"Dockerfile does not exist: {dockerfile}")

    try:
        subprocess.run(
            [
                "docker",
                "build",
                "--tag",
                image,
                str(context),
            ],
            check=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "Docker CLI is required to build the FastAPI victim image."
        ) from error
