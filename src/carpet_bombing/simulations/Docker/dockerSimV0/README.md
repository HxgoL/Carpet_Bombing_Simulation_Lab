# Simulation Docker V0 - Carpet Bombing

Ce dossier contient un petit laboratoire Docker pour generer du trafic reseau vers plusieurs victimes et enregistrer les captures au format pcap.

## Architecture

Le fichier `docker-compose.yml` demarre les services suivants sur le reseau Docker `lab_net` :

| Service | Conteneur | IP | Role |
| --- | --- | --- | --- |
| `attacker` | `cb_attacker` | `10.10.0.10` | Genere le trafic avec Scapy ou HTTP |
| `monitor` | `cb_monitor` | `10.10.0.20` | Capture le trafic avec `tcpdump` |
| `victim01` a `victim16` | `cb_victim01` a `cb_victim16` | `10.10.0.101` a `10.10.0.116` | Cibles de la simulation |

Les fichiers generes sont ecrits dans le dossier local `data/`, monte dans les conteneurs via `/app/data`.

## Prerequis

Installer et lancer Docker Desktop :

- Docker Desktop pour Windows
- WSL2 active si Docker Desktop le demande
- PowerShell relance apres l'installation

Verifier que Docker est disponible :

```powershell
docker --version
docker compose version
```

Si PowerShell affiche `docker : Le terme "docker" n'est pas reconnu`, Docker Desktop n'est pas installe, pas lance, ou pas disponible dans le `PATH`.

## Demarrage du lab

Se placer dans ce dossier :

```powershell
cd "D:\Cours\EIDD\S8\Stage\Carpet_Bombing_Simulation_Lab\src\carpet_bombing\simulations\Docker\dockerSimV0"
```

Construire les images :

```powershell
docker compose build
```

Demarrer les conteneurs :

```powershell
docker compose up -d
```

Verifier que les conteneurs tournent :

```powershell
docker compose ps
```

## Lancer une capture pcap

Demarrer la capture depuis le conteneur `monitor` :

```powershell
docker exec -d cb_monitor /app/capture.sh carpet_bombing
```

Le script `monitor/capture.sh` capture sur l'interface `eth0` par defaut et ecrit les fichiers dans :

```text
data/pcaps/
```

Un lien `data/pcaps/latest.pcap` pointe vers la derniere capture.

## Generer du trafic carpet bombing

Lancer le trafic depuis le conteneur attaquant :

```powershell
docker exec cb_attacker python /app/generate_traffic.py `
  --scenario carpet_bombing `
  --duration 60 `
  --rate 100 `
  --protocol tcp `
  --targets 10.10.0.101-10.10.0.116 `
  --fanout 16 `
  --randomize-targets
```

Parametres importants :

| Option | Description |
| --- | --- |
| `--scenario` | `normal`, `ddos_single` ou `carpet_bombing` |
| `--duration` | Duree de la simulation en secondes |
| `--rate` | Debit moyen en paquets ou requetes par seconde |
| `--protocol` | `icmp`, `tcp`, `udp` ou `http` |
| `--targets` | IPs cibles ou plage d'IPs |
| `--fanout` | Nombre de victimes utilisees |
| `--randomize-targets` | Melange l'ordre des cibles |
| `--packet-size` | Taille des paquets pour ICMP/TCP/UDP |
| `--dst-port` | Port de destination pour TCP/UDP/HTTP |

## Arreter la capture

Arreter proprement `tcpdump` :

```powershell
docker exec cb_monitor pkill -INT tcpdump
```

Verifier les fichiers generes :

```powershell
Get-ChildItem .\data\pcaps
Get-ChildItem .\data\logs
```

## Scenarios utiles

Trafic normal limite :

```powershell
docker exec cb_attacker python /app/generate_traffic.py `
  --scenario normal `
  --duration 30 `
  --rate 10 `
  --protocol http `
  --targets 10.10.0.101-10.10.0.116
```

DDoS vers une seule victime :

```powershell
docker exec cb_attacker python /app/generate_traffic.py `
  --scenario ddos_single `
  --duration 60 `
  --rate 200 `
  --protocol tcp `
  --targets 10.10.0.101-10.10.0.116
```

Carpet bombing en rafales UDP :

```powershell
docker exec cb_attacker python /app/generate_traffic.py `
  --scenario carpet_bombing `
  --duration 60 `
  --rate 100 `
  --protocol udp `
  --targets 10.10.0.101-10.10.0.116 `
  --fanout 16 `
  --randomize-targets `
  --burst-mode `
  --burst-size 100 `
  --burst-interval 1
```

## Changer le mode des victimes

Par defaut, les victimes lancent `nginx` sur le port 80.

Modes disponibles dans `victim/entrypoint.sh` :

- `nginx`
- `iperf3`
- `python_http`

Exemple avec le serveur HTTP Python :

```powershell
$env:VICTIM_MODE="python_http"
docker compose up -d --build
```

Revenir au mode par defaut :

```powershell
Remove-Item Env:\VICTIM_MODE
docker compose up -d --build
```

## Nettoyage

Arreter les conteneurs :

```powershell
docker compose down
```

Supprimer aussi le reseau et les conteneurs recreables :

```powershell
docker compose down --remove-orphans
```

Supprimer les captures locales :

```powershell
Remove-Item -Recurse -Force .\data
```

## Depannage

### `docker` n'est pas reconnu

Docker n'est pas disponible dans PowerShell.

Actions possibles :

1. Installer Docker Desktop.
2. Lancer Docker Desktop.
3. Attendre que Docker soit pret.
4. Fermer puis rouvrir PowerShell.
5. Relancer `docker --version`.

### Aucun pcap n'est cree

Verifier que la capture tourne :

```powershell
docker logs cb_monitor
```

Verifier que `tcpdump` est actif :

```powershell
docker exec cb_monitor ps aux
```

Verifier que du trafic est bien genere :

```powershell
docker logs cb_attacker
```

### Permission refusee pour capturer

Le service `monitor` doit avoir les capacites reseau dans `docker-compose.yml` :

```yaml
cap_add:
  - NET_ADMIN
  - NET_RAW
```

Ces capacites sont deja presentes dans la configuration actuelle.

## Fichiers principaux

| Fichier | Role |
| --- | --- |
| `docker-compose.yml` | Declare le lab Docker, les IPs et les volumes |
| `attacker/generate_traffic.py` | Genere le trafic de simulation |
| `attacker/Dockerfile` | Image de l'attaquant |
| `monitor/capture.sh` | Lance la capture `tcpdump` |
| `monitor/dockerfile` | Image du moniteur |
| `victim/entrypoint.sh` | Lance le service des victimes |
| `victim/dockerfile` | Image des victimes |
