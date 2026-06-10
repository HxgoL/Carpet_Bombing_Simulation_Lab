FROM python:3.12-slim

WORKDIR /service

# Ces outils rendent l'image compatible avec Containernet et avec les scripts
# de trafic existants : bash, ip, ping, pkill et timeout.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        bash \
        coreutils \
        iproute2 \
        iputils-ping \
        procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /service/requirements.txt
RUN pip install --no-cache-dir --requirement /service/requirements.txt

COPY app /service/app

EXPOSE 8000

# Containernet reçoit la commande du service avec ``dcmd``. Garder un CMD
# neutre évite de lancer une seconde instance d'Uvicorn lors de net.start().
CMD ["/bin/bash"]
