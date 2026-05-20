# Simulation V3

Cette version reprend la V2 et ajoute :

- plusieurs attaquants
- des cibles actives et inactives
- une commande automatique pour lancer les attaques en même temps

## Topologie

```text
attaquants -> switch attaquants -> gateway -> switch victimes -> victimes
```

Le lien entre la gateway et le switch victimes reste limité avec `TCLink` :

```text
gateway -> switch victimes : 5 Mbit/s, 10 ms, 0% perte
```

## Adressage

```text
Réseau victimes : 10.0.0.0/24
Victimes actives : 10.0.0.1-10.0.0.8
IP inactives ciblées : 10.0.0.9-10.0.0.40
Gateway côté victimes : 10.0.0.254

Réseau attaquants : 10.0.1.0/24
Attaquants : 10.0.1.1-10.0.1.4
Gateway côté attaquants : 10.0.1.254
```

## Lancer la topologie

Terminal 1 :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v3/topology/multi_attacker_tclink_topology.py
```

## Capturer le trafic

Terminal 2 :

```bash
mkdir -p src/carpet_bombing/simulations/simulation_v3/pcaps

timeout 45 sudo tcpdump -i any \
  -w src/carpet_bombing/simulations/simulation_v3/pcaps/carpet_multi_attacker_inactive_v3.pcap \
  'net 10.0.0.0/24 or net 10.0.1.0/24'
```

## Lancer l'attaque automatiquement

Dans la console Mininet :

```bash
start_attack
```

Cette commande lance les attaques depuis `a1`, `a2`, `a3` et `a4` pendant 30
secondes. Chaque attaquant cible une partie différente du sous-réseau.

Les cibles sont :

```text
a1 -> 10.0.0.1-10.0.0.10
a2 -> 10.0.0.11-10.0.0.20
a3 -> 10.0.0.21-10.0.0.30
a4 -> 10.0.0.31-10.0.0.40
```

Ces plages contiennent :

- les victimes actives `10.0.0.1-10.0.0.8`
- les IP inactives `10.0.0.9-10.0.0.40`

## Arrêter l'attaque

```bash
stop_attack
```

## Vérifier la congestion du lien

Dans la console Mininet :

```bash
gw tc -s qdisc show dev gw-eth1
```

Les compteurs importants sont :

- `overlimits`
- `dropped`
- `backlog`

## Objectif

La V3 permet de produire une capture plus représentative d'un carpet bombing :

```text
plusieurs sources attaquantes
dispersion sur le préfixe victime
trafic vers des adresses actives et inactives
lien victime limité par TCLink
```
