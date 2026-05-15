# Simulation V1

Cette version ajoute une gateway et deux sous-réseaux :

```text
attaquant(s) -> switch attaquants -> gateway -> switch victimes -> victimes
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
sudo python3 src/carpet_bombing/simulations/simulation_v1/topology/gateway_topology.py
```

Le trafic normal entre les victimes démarre automatiquement. Il est volontairement
lent pour rester lisible dans l'interface, et chaque victime a son propre rythme
d'envoi.

## Tester la connectivité

Dans la console Mininet :

```bash
a1 ping -c 3 10.0.0.1
```

## Lancer une attaque simple

Dans la console Mininet :

```bash
a1 python3 src/carpet_bombing/simulations/simulation_v1/traffic_generator/carpet_bombing_attack.py \
  --targets 10.0.0.1-10.0.0.8 \
  --packet-count 500 \
  --delay 0 \
  --payload-size 512 \
  --protocol UDP
```

Le script est paramétrable pour préparer la future UI : nombre de paquets,
vitesse d'envoi, protocole et cibles.

Par défaut, l'attaque n'est pas infinie :

```text
500 paquets UDP sans pause entre les paquets
```

Pour une attaque plus forte :

```bash
a1 python3 src/carpet_bombing/simulations/simulation_v1/traffic_generator/carpet_bombing_attack.py \
  --targets 10.0.0.1-10.0.0.8 \
  --packet-count 2000 \
  --delay 0.001 \
  --payload-size 1024 \
  --protocol UDP
```
