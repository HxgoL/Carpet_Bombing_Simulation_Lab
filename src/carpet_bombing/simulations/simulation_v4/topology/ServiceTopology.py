from pathlib import Path
import subprocess

API_IMAGE = "carpet-bombing-fastapi:v4"
API_SERVER_DIR = Path(__file__).resolve().parents[1] / "servers" / "fastapi"


def build_api_image():
    subprocess.run(
        ["docker", "build", "-t", API_IMAGE, str(API_SERVER_DIR)],
        check=True,
    )