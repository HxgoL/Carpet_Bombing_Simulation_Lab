# Simulation V2

Cette version reprend la topologie V1 et ajoute un lien limité avec `TCLink`.

Objectif :

```text
observer l'effet d'une attaque carpet bombing quand le lien vers le réseau victime
devient un goulot d'étranglement.
```

## Topologie

```text
attaquant(s) -> switch attaquants -> gateway -> switch victimes -> victimes
```

La différence avec la V1 est le lien entre la gateway et le switch victimes :

```text
gateway -> switch victimes : 5 Mbit/s, 10 ms, 0% perte
```

## Adressage

```text
Réseau victimes : 10.0.0.0/24
Gateway côté victimes : 10.0.0.254

Réseau attaquants : 10.0.1.0/24
Gateway côté attaquants : 10.0.1.254
```

## Lancer la topologie

Terminal 1 :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v2/topology/gateway_tclink_topology.py
```

Le trafic normal entre les victimes démarre automatiquement, comme dans la V1.

## Capturer le trafic

Terminal 2 :

```bash
mkdir -p src/carpet_bombing/simulations/simulation_v2/pcaps

sudo tcpdump -i any \
  -w src/carpet_bombing/simulations/simulation_v2/pcaps/carpet_udp_v2_limited_link.pcap \
  'net 10.0.0.0/24 or net 10.0.1.0/24'
```

## Tester la connectivité

Dans la console Mininet :

```bash
a1 ping -c 10 10.0.0.1
```

Cette commande permet d'observer la latence de base vers une victime.

## Lancer une attaque

Dans la console Mininet :

```bash
a1 python3 src/carpet_bombing/simulations/simulation_v2/traffic_generator/carpet_bombing_attack.py \
  --targets 10.0.0.1-10.0.0.8 \
  --packet-count 3000 \
  --delay 0 \
  --payload-size 1024 \
  --protocol UDP
```

Quand l'attaque est terminée, arrêter `tcpdump` avec `Ctrl+C`.

## Comparaison attendue

La V2 doit permettre de comparer :

```text
V1 : attaque visible mais lien non contraint
V2 : attaque visible sur un lien limité
```

Les métriques importantes sont :

- débit en paquets par seconde
- volume reçu par destination
- dispersion des destinations
- latence ping avant et pendant l'attaque

## Note

Cette version ne fait pas encore de mitigation. Elle prépare un scénario de
congestion qui pourra ensuite servir à tester la mitigation côté gateway.
