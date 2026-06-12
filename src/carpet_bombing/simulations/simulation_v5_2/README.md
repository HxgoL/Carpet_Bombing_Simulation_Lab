# Simulation V5.2

Cette version conserve l'architecture modulaire Paris -> Canada, puis reprend
les bons apports de la V5 officielle : comparaison normal / DDoS single-target
/ carpet bombing, attaque avancée, TTL variable et rotation contrôlée des IP
sources.

La V5 officielle reste inchangée. La V5.2 introduit :

- une topologie géographique simplifiée Paris -> transit -> Canada
- plusieurs machines attaquantes côté Paris
- des sources IP spoofées qui changent pendant l'attaque
- une attaque carpet bombing fragmentée avec Scapy
- une boucle de réception UDP/TCP sur les victimes actives
- un réseau victime canadien avec des IP actives et inactives
- une comparaison entre attaque single-target et carpet bombing
- des TTL variables pour simuler des chemins d'origine différents
- un mode `dns_amp` en plus de `icmp`, `udp`, `tcp_syn` et `mixed`
- des captures et labels séparés pour produire un dataset reproductible

## Architecture

La V5 suit l'architecture modulaire proposée pour le cyber range :

```text
simulation_v5_2/
├── main.py
├── config/
├── topology/
├── networks/
├── nodes/
├── services/
├── monitoring/
├── traffic/
├── attacks/
├── dataset/
├── experiments/
└── pcaps/
```

Les dossiers prévus pour des phases futures (`defense`, `rl_env`, `gns3`,
`docker`, `scenarios`) ne sont pas créés dans cette version tant qu'ils ne
contiennent pas de code utile.

Répartition actuelle :

- `main.py` : point d'entrée de la simulation
- `config/settings.py` : IPs, durées, plages d'attaque, liens réseau
- `topology/` : assemblage du lab, routage et nettoyage
- `networks/` : construction des sous-réseaux Paris, transit et Canada
- `nodes/` : types de noeuds, dont les routeurs Linux
- `services/` : services Docker côté Canada
- `traffic/` : trafic normal, récepteurs et orchestration du trafic légitime
- `attacks/` : générateur avancé fragmenté, découpé par responsabilité, et orchestrateur
- `dataset/` : emplacement prévu pour les exports de features
- `experiments/` : captures et labels de dataset
- `pcaps/` : captures réseau brutes générées

## Topologie

```text
Paris attacker LAN
  10.10.0.0/24
        |
   r_paris
        |
  lien Paris/transit
        |
   r_atlantic
        |
  lien transatlantique limité
        |
   r_canada
        |
Canada victim DMZ
  10.20.0.0/24
```

Le chemin est volontairement routé par plusieurs noeuds pour pouvoir observer
un comportement proche d'un traceroute :

```bash
a1 traceroute -n 10.20.0.10
```

## Adressage

```text
Réseau attaquants Paris : 10.10.0.0/24
Gateway Paris : 10.10.0.254
Attaquants : 10.10.0.1-10.10.0.4

Transit Paris -> Atlantic : 172.16.0.0/30
Transit Atlantic -> Canada : 172.16.0.4/30

Réseau victimes Canada : 10.20.0.0/24
Gateway Canada : 10.20.0.254
```

Victimes actives :

```text
10.20.0.10-10.20.0.14
10.20.0.30-10.20.0.34
10.20.0.50-10.20.0.54
10.20.0.70-10.20.0.74
```

L'attaque cible aussi des IP non créées dans Mininet afin de garder l'effet
carpet bombing sur un préfixe entier.

## Générateur d'attaque avancée

Le générateur V5.2 reprend les idées du code transmis par le tuteur et de la
V5 officielle :

- `--dst-ip` : cible unique pour comparer avec un DDoS classique
- `--dst-range` : plage de victimes ciblées
- `--src-ip`, `--src-range` ou `--src-ips` : sources forgées
- `--duration` : durée de l'attaque
- `--pps` : débit avant fragmentation
- `--protocol` : `icmp`, `udp`, `tcp_syn`, `dns_amp` ou `mixed`
- `--fragment-mode manual` : fragmentation Scapy avec `fragment()`
- `--fragsize` : taille des fragments IP
- `--payload-size` : taille du payload avant fragmentation
- `--ttl-min` / `--ttl-max` : TTL variable
- `--src-rotation-interval` : changement périodique d'IP source

Le générateur est organisé en trois couches simples :

- entrée : `fragmented_carpet_bombing.py` lit la CLI et construit la configuration
- domaine : `attack_config.py`, `ip_parsing.py`, `packet_factory.py` et
  `source_rotation.py` décrivent et fabriquent l'attaque
- infrastructure : `traffic_sender.py` fragmente et envoie les paquets avec Scapy

Scapy reste adapté aux attaques IP/ICMP/UDP/TCP et à la fragmentation. Un trafic
HTTP réaliste devra être ajouté comme scénario applicatif séparé, en ciblant les
services de `services/canada_services.py`, plutôt que comme un faux paquet HTTP
dans le générateur réseau.

Exemple manuel dans la console Mininet :

```bash
a1 python3 src/carpet_bombing/simulations/simulation_v5_2/attacks/fragmented_carpet_bombing.py \
  --dst-range 10.20.0.1-10.20.0.80 \
  --src-range 10.10.1.1-10.10.1.250 \
  --duration 30 \
  --pps 200 \
  --protocol mixed \
  --fragment-mode manual
```

## Lancer la topologie seule

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_2/main.py
```

Mode DDoS single-target automatique :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_2/main.py \
  --auto-scenario single_target \
  --duration 45 \
  --attack-duration 30 \
  --warmup 5
```

Mode carpet bombing automatique :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_2/main.py \
  --auto-scenario carpet \
  --duration 45 \
  --attack-duration 30 \
  --warmup 5
```

## Lancer une expérience complète

Capture normale :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_2/experiments/run_v5_experiment.py \
  --scenario normal
```

Capture avec attaque single-target :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_2/experiments/run_v5_experiment.py \
  --scenario single_target
```

Capture avec carpet bombing :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_2/experiments/run_v5_experiment.py \
  --scenario carpet
```

Les deux scénarios :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5_2/experiments/run_v5_experiment.py \
  --scenario all
```

## Lien avec le document d'architecture

La V5 suit une approche incrémentale :

- une simulation exécutable seule
- des fichiers séparés pour la topologie, le trafic, l'attaque et les labels
- une baseline normale pour comparer les faux positifs
- un scénario DDoS single-target pour comparer avec le carpet bombing
- des métadonnées de capture dans `experiments/labels_v5.json`
- une base compatible avec une future extension monitoring/dataset/RL
