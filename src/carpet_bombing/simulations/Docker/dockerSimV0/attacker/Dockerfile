#Ce fichier décrit comment construire l'image docker d'attacker
# voir comme: recette de fabrication de l’environnement attaquant

# Utiliser une image de base Python légère
FROM python:3.11-slim

#installer les outils nécessaires pour le trafic réseau et le débogage
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping curl tcpdump \
    && rm -rf /var/lib/apt/lists/*

#définir le répertoire de travail dans le conteneur
WORKDIR /app #equiv cd /app

#installer les bibliothèques python nécessaires pour générer le trafic
RUN pip install --no-cache-dir scapy requests pyyaml

#copier le script de génération de trafic dans le conteneur
COPY generate_traffic.py /app/generate_traffic.py

#
CMD ["sleep", "infinity"]