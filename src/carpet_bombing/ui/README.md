# UI Traffic Visualizer

## Lancer la simulation V0.1

Terminal 1 :

```bash
sudo python3 src/carpet_bombing/simulations/simulation_v0.1/topology/basic_topology.py
```

## Lancer le visualiseur

Terminal 2 :

```bash
sudo python3 src/carpet_bombing/ui/traffic_visualizer.py --interface any --debug
```

## Ouvrir l'interface

Dans le navigateur :

```text
http://127.0.0.1:8765
```

Pour générer du trafic visible depuis la console Mininet :

```bash
pingall
```
