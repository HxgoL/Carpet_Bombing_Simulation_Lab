# Simulation V4

Cette version reprend la V3 et rapproche la topologie d'un scénario final :

- plusieurs attaquants
- 20 victimes actives réparties dans le préfixe victime
- des IP inactives dans chaque plage ciblée
- un lien limité conservé avec `TCLink`
- des noms de captures et labels définis dans `experiments/labels_v4.json`

## Topologie

```text
attaquants -> switch attaquants -> gateway -> switch victimes -> victimes
```

Le lien entre la gateway et le switch victimes reste limité :

```text
gateway -> switch victimes : 5 Mbit/s, 10 ms, 0% perte
```

## Adressage

```text
Réseau victimes : 10.0.0.0/24
Gateway côté victimes : 10.0.0.254

Réseau attaquants : 10.0.1.0/24
Attaquants : 10.0.1.1-10.0.1.4
Gateway côté attaquants : 10.0.1.254
```

Victimes actives :

```text
10.0.0.1-10.0.0.5
10.0.0.21-10.0.0.25
10.0.0.41-10.0.0.45
10.0.0.61-10.0.0.65
```

Cibles par attaquant :

```text
a1 -> 10.0.0.1-10.0.0.20
a2 -> 10.0.0.21-10.0.0.40
a3 -> 10.0.0.41-10.0.0.60
a4 -> 10.0.0.61-10.0.0.80
```

## Lancer une expérience complète

Le script d'expérience lance automatiquement :

- `tcpdump`
- la topologie Mininet
- le scénario normal ou attaque
- l'arrêt de la capture

Capture normale :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v4/experiments/run_v4_experiment.py \
  --scenario normal
```

Capture avec attaque :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v4/experiments/run_v4_experiment.py \
  --scenario attack
```

Les deux scénarios à la suite :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v4/experiments/run_v4_experiment.py \
  --scenario all
```

Les durées peuvent être changées sans modifier les fichiers :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v4/experiments/run_v4_experiment.py \
  --scenario attack \
  --duration 60 \
  --attack-duration 40 \
  --warmup 5
```

## Lancer la topologie seule

La topologie peut aussi être lancée seule pour faire des tests manuels :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v4/topology/final_like_tclink_topology.py
```

Mode normal automatique :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v4/topology/final_like_tclink_topology.py \
  --auto-scenario normal \
  --duration 45
```

Mode attaque automatique :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v4/topology/final_like_tclink_topology.py \
  --auto-scenario attack \
  --duration 45 \
  --attack-duration 30 \
  --warmup 5
```

Sans `--auto-scenario`, la topologie ouvre la console Mininet :

```bash
start_attack
stop_attack
```

## Vérifier la congestion

Dans la console Mininet :

```bash
gw tc -s qdisc show dev gw-eth1
```

## Labels

Les labels et paramètres de capture sont décrits dans :

```text
src/carpet_bombing/simulations/simulation_v4/experiments/labels_v4.json
```
