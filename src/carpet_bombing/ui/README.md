# UI Traffic Visualizer

## Lancer la simulation V1

Terminal 1 :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v1/topology/gateway_topology.py
```

## Lancer le visualiseur

Terminal 2 :

```bash
sudo python3 src/carpet_bombing/ui/traffic_visualizer.py --simulation v1 --interface any --debug
```

## Ouvrir l'interface

Dans le navigateur :

```text
http://127.0.0.1:8765
```

Pour générer du trafic visible depuis la console Mininet :

```bash
a1 python3 src/carpet_bombing/simulations/simulation_v1/traffic_generator/carpet_bombing_attack.py \
  --targets 10.0.0.1-10.0.0.8 \
  --packet-count 500 \
  --delay 0 \
  --payload-size 512 \
  --protocol UDP
```

Pour revoir la simulation V0.1 :

```bash
sudo python3 src/carpet_bombing/ui/traffic_visualizer.py --simulation v0.1 --interface any --debug
```
