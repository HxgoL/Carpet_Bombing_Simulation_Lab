# Simulation V5

Cette version ajoute un générateur de carpet bombing plus réaliste, inspiré du générateur fragmenté proposé pendant la réunion.

La V5 ne contient pas encore Docker. Elle complète la V4 avec :

- fragmentation IP ;
- topologie multi-routeurs avec routage statique ;
- TTL configurable ;
- variation des IP sources simulées avec des plages réservées aux tests ;
- changement d'IP source toutes les 5 secondes par défaut ;
- plusieurs protocoles d'attaque : UDP, TCP SYN, ICMP, DNS amplification simulée et trafic mixte ;
- ports ciblés configurables pour représenter des services disponibles ou non disponibles.
- un scénario DDoS classique sur une seule IP ;
- un scénario carpet bombing avancé sur un préfixe.

## Objectif

La V5 sert à produire des captures plus riches pour la caractérisation, la détection et la mitigation.

Elle permet notamment d'observer :

- la dispersion source-destination ;
- le passage par plusieurs routeurs simulés ;
- les paquets fragmentés ;
- les variations de TTL ;
- les attaques vers des IP actives et inactives ;
- les ports et services ciblés.

## Scénarios

Le runner V5 permet de choisir le scénario :

```text
normal        : trafic normal uniquement
single_target : trafic normal + DDoS concentré sur 10.0.0.1
carpet        : trafic normal + carpet bombing avancé sur 10.0.0.1-10.0.0.80
all           : lance les trois captures à la suite
```

Les scénarios d'attaque gardent le trafic normal en arrière-plan. Cela permet d'obtenir des captures plus réalistes pour la détection et la mitigation.

## Topologie

```text
a1, a2 -> switch attaquant 1 -> r1
                                      \
                                       r_core -> gw -> switch victimes -> victimes
                                      /
a3, a4 -> switch attaquant 2 -> r2
```

Réseaux utilisés :

```text
attaquants groupe 1 : 10.0.1.0/24
attaquants groupe 2 : 10.0.2.0/24
liens inter-routeurs : 10.10.0.0/16
victimes : 10.0.0.0/24
```

Le lien `gw -> victimes` reste limité avec `TCLink`.

Les hôtes attaquants gardent des IP routables dans Mininet, mais les paquets d'attaque peuvent utiliser des IP sources simulées :

```text
192.0.2.0/24
198.51.100.0/24
203.0.113.0/24
```

Ces plages sont réservées aux exemples et aux tests. Elles permettent de simuler des sources externes sans utiliser de vraies IP publiques.

Les victimes actives sont réparties de façon non uniforme dans `10.0.0.1-10.0.0.80`. Les autres adresses de la plage restent inactives et peuvent donc être ciblées par le carpet bombing.

## Lancer les captures

Capture complète :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5/experiments/run_v5_experiment.py \
  --scenario all
```

Capture carpet bombing uniquement :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5/experiments/run_v5_experiment.py \
  --scenario carpet \
  --duration 45 \
  --attack-duration 30 \
  --warmup 5
```

Capture DDoS sur une seule IP :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v5/experiments/run_v5_experiment.py \
  --scenario single_target \
  --duration 45 \
  --attack-duration 30 \
  --warmup 5
```

## Générateur avancé

Fichier :

```text
traffic_generator/advanced_carpet_bombing_attack.py
```

Exemple manuel dans Mininet :

```bash
a1 python3 src/carpet_bombing/simulations/simulation_v5/traffic_generator/advanced_carpet_bombing_attack.py \
  --dst-range 10.0.0.1-10.0.0.80 \
  --src-ips 192.0.2.10,198.51.100.20,203.0.113.30 \
  --duration 30 \
  --pps 100 \
  --protocol mixed \
  --payload-size 4000 \
  --fragment-mode manual \
  --fragsize 300 \
  --ttl-min 40 \
  --ttl-max 64 \
  --src-rotation-interval 5
```

Exemple DDoS sur une seule IP :

```bash
a1 python3 src/carpet_bombing/simulations/simulation_v5/traffic_generator/advanced_carpet_bombing_attack.py \
  --dst-ip 10.0.0.1 \
  --src-ips 192.0.2.10,198.51.100.20,203.0.113.30 \
  --duration 30 \
  --pps 100 \
  --protocol mixed \
  --payload-size 4000 \
  --fragment-mode manual \
  --fragsize 300 \
  --ttl-min 40 \
  --ttl-max 64 \
  --src-rotation-interval 5
```

## Protocoles disponibles

```text
icmp
udp
tcp_syn
dns_amp
mixed
```

`dns_amp` simule des réponses UDP volumineuses venant de ports de services d'amplification, par exemple DNS ou NTP.

## Modes de fragmentation

```text
manual : fragmente les paquets avec Scapy avant l'envoi
auto   : envoie le paquet complet et laisse la pile réseau gérer si possible
none   : désactive la fragmentation volontaire
```

## Remarque

Les IP sources variables sont simulées avec Scapy. Elles doivent être utilisées uniquement dans l'environnement de laboratoire.
