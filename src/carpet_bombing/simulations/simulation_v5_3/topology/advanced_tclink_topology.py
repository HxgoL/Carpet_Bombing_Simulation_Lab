"""Point d'entrée rétrocompatible de la topologie V5.3.

La composition de l'application se trouve dans ``presentation.main``. Ce
wrapper conserve le chemin exécuté par le runner d'expériences existant.
"""

from __future__ import annotations

import sys
from pathlib import Path


# Un lancement direct de ce fichier n'ajoute pas automatiquement ``src`` au
# chemin d'import Python.
SOURCE_DIRECTORY = Path(__file__).resolve().parents[4]

if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))


from carpet_bombing.simulations.simulation_v5_3.presentation.main import main


if __name__ == "__main__":
    main()
