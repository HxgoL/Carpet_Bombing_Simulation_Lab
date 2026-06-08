# Simulation V5.3

La simulation V5.3 est un laboratoire réseau destiné à l'étude du carpet
bombing DDoS, de sa caractérisation et de sa détection.

Elle propose la même topologie et les mêmes scénarios avec deux backends :

```text
mininet      : victimes classiques dans des namespaces réseau
containernet : victimes Docker exécutant un serveur FastAPI
```

Le backend Mininet reste le choix par défaut. Le backend Containernet permet
d'ajouter progressivement des services applicatifs réalistes sans modifier la
logique des scénarios.

## Fonctionnalités

- topologie multi-routeurs avec routage statique ;
- lien limité vers le réseau des victimes avec `TCLink` ;
- trafic normal conservé pendant les attaques ;
- attaques single-target et carpet bombing ;
- protocoles ICMP, UDP, TCP SYN, DNS amplification simulée et trafic mixte ;
- fragmentation IP configurable ;
- variation du TTL et rotation des IP sources simulées ;
- victimes actives et adresses inactives dans la plage ciblée ;
- victimes Docker FastAPI avec le backend Containernet ;
- génération automatisée de captures PCAP.

Les IP sources simulées utilisent uniquement des plages réservées aux exemples
et aux tests. Cette simulation doit rester dans un environnement de laboratoire.

## Topologie

```text
a1, a2 -> s1 -> r1
                    \
                     r_core -> gw -> s3 -> victimes
                    /
a3, a4 -> s2 -> r2
```

Réseaux utilisés :

```text
attaquants groupe 1 : 10.0.1.0/24
attaquants groupe 2 : 10.0.2.0/24
liens inter-routeurs : 10.10.0.0/16
victimes              : 10.0.0.0/24
```

Le lien `gw -> s3` est limité par défaut à :

```text
bande passante : 5 Mbit/s
délai          : 10 ms
perte          : 0 %
```

Les 20 victimes actives sont réparties de manière non uniforme entre
`10.0.0.1` et `10.0.0.80`. Les autres adresses restent inactives mais peuvent
être ciblées par le carpet bombing.

## Scénarios

```text
normal        : trafic normal uniquement
single_target : trafic normal + DDoS concentré sur 10.0.0.1
carpet        : trafic normal + attaque distribuée sur 10.0.0.1-10.0.0.80
```

Le runner d'expériences accepte aussi :

```text
all : exécute successivement normal, single_target et carpet
```

## Architecture

```text
simulation_v5_3/
├── domain/                   modèles et règles métier
├── config/                   valeurs par défaut et factory
├── application/              orchestration indépendante des backends
├── infrastructure/
│   ├── mininet/              adaptateurs Mininet
│   ├── containernet/         adaptateurs Containernet
│   └── docker/               construction de l'image FastAPI
├── presentation/             arguments CLI et assemblage des dépendances
├── services/fastapi_server/  service embarqué dans les victimes Docker
├── topology/                 point d'entrée historique
├── experiments/              captures PCAP automatisées
└── traffic_generator/        générateurs de trafic existants
```

Les couches `domain/` et `application/` ne dépendent ni de Mininet, ni de
Containernet, ni de Docker, ni de FastAPI.

Les deux backends réutilisent les mêmes :

- `SimulationConfig` ;
- routes ;
- services applicatifs ;
- scénarios ;
- scripts de `traffic_generator/`.

## Prérequis

Prérequis communs :

- Linux ;
- Python 3.12 ;
- privilèges root ;
- `tcpdump` pour les captures ;
- outils réseau Linux nécessaires à Mininet.

Backend Mininet :

- Mininet ;
- Open vSwitch.

Backend Containernet :

- Containernet ;
- Docker fonctionnel ;
- Open vSwitch.

Le backend Containernet construit automatiquement l'image suivante si elle
n'existe pas localement :

```text
carpet-bombing-fastapi-v5-3:latest
```

## Lancer la topologie

Les commandes suivantes doivent être exécutées depuis la racine du dépôt.

### Mininet interactif

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_3/topology/advanced_tclink_topology.py \
  --backend mininet
```

### Containernet interactif

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_3/topology/advanced_tclink_topology.py \
  --backend containernet
```

### Scénario Mininet automatique

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_3/topology/advanced_tclink_topology.py \
  --backend mininet \
  --auto-scenario carpet \
  --duration 45 \
  --attack-duration 30 \
  --warmup 5 \
  --pps 120 \
  --protocol mixed \
  --fragment-mode manual
```

### Scénario Containernet automatique

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_3/topology/advanced_tclink_topology.py \
  --backend containernet \
  --auto-scenario carpet \
  --duration 45 \
  --attack-duration 30 \
  --warmup 5
```

## Options principales

```text
--backend          mininet | containernet
--auto-scenario    normal | single_target | carpet
--duration         durée totale du scénario en secondes
--attack-duration  durée transmise au générateur d'attaque
--warmup           trafic normal avant le début de l'attaque
--pps              paquets d'attaque par seconde et par attaquant
--protocol         icmp | udp | tcp_syn | dns_amp | mixed
--fragment-mode    manual | auto | none
```

## Commandes interactives

Les commandes personnalisées suivantes sont disponibles dans la CLI :

```text
start_single_target_attack
start_carpet_attack
stop_attack
```

Exemples de commandes réseau :

```text
a1 traceroute -n 10.0.0.1
gw tc -s qdisc show dev gw-eth1
h1 ip route
```

## Victimes Docker FastAPI

Avec le backend Containernet, chaque victime est un conteneur Docker exécutant
un serveur FastAPI sur le port `8000`.

Endpoints disponibles :

```text
GET /health
GET /workload/light
GET /workload/cpu?duration_ms=50
GET /metrics
```

Exemples depuis la CLI Containernet :

```text
a1 curl http://10.0.0.1:8000/health
a1 curl http://10.0.0.1:8000/workload/light
a1 curl "http://10.0.0.1:8000/workload/cpu?duration_ms=100"
a1 curl http://10.0.0.1:8000/metrics
```

`/workload/cpu` accepte une durée comprise entre `1` et `1000` millisecondes.
Les métriques sont conservées en mémoire dans chaque conteneur.

Les scripts de `traffic_generator/` sont montés en lecture seule dans les
victimes Docker au même chemin absolu que sur l'hôte. `TrafficService` peut
ainsi fonctionner sans connaître Docker.

## Lancer les captures

### Tous les scénarios avec Mininet

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_3/experiments/run_v5_experiment.py \
  --backend mininet \
  --scenario all
```

### Capture carpet avec Containernet

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_3/experiments/run_v5_experiment.py \
  --backend containernet \
  --scenario carpet \
  --duration 45 \
  --attack-duration 30 \
  --warmup 5 \
  --pps 120 \
  --protocol mixed \
  --fragment-mode manual
```

Les captures sont écrites dans :

```text
simulation_v5_3/pcaps/
```

## Générateur d'attaque

Le générateur avancé reste :

```text
traffic_generator/advanced_carpet_bombing_attack.py
```

Modes de fragmentation :

```text
manual : fragmentation volontaire avec Scapy
auto   : délégation éventuelle à la pile réseau
none   : aucune fragmentation volontaire
```

Plages de sources simulées :

```text
192.0.2.0/24
198.51.100.0/24
203.0.113.0/24
198.18.0.0/15
```

## Tests

Lancer les tests de la simulation V5.3 :

```bash
poetry run pytest tests/simulation_v5_3 -v
```

Lancer tous les tests du dépôt :

```bash
poetry run pytest
```

Les futurs tests nécessitant réellement Containernet, Docker et les privilèges
root doivent utiliser le marqueur :

```python
@pytest.mark.containernet
```

## Limites actuelles

- les métriques FastAPI sont uniquement conservées en mémoire ;
- les processus sont arrêtés avec `pkill -f` plutôt qu'avec des PID suivis ;
- le backend Containernet nécessite une machine Linux configurée avec Docker ;
- la construction et l'exécution réelles de Containernet ne sont pas
  vérifiables depuis un environnement Windows sans Docker et Containernet.
