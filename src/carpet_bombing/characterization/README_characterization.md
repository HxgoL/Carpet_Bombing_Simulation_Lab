# Characterization

Ce dossier contient la partie **caractérisation du trafic réseau**.

L’objectif est d’analyser les captures `.pcap` / `.pcapng` générées pendant les simulations afin de comprendre les différences entre :

- trafic normal ;
- DDoS classique vers une seule IP ;
- attaque DDoS de type carpet bombing.

## Rôle

La caractérisation permet d’extraire des métriques utiles pour la détection, la mitigation et le rapport final.

Exemples de métriques :

- nombre de paquets par seconde ;
- volume de trafic par seconde ;
- IP sources et destinations les plus fréquentes ;
- répartition TCP / UDP / ICMP ;
- nombre d’IP destinations ciblées ;
- fan-out sur le préfixe réseau.

## Sorties attendues

Les résultats seront stockés dans :

```text
results/characterization/
```

Ils pourront contenir :

- fichiers CSV ;
- statistiques ;
- graphiques ;
- observations pour le rapport final.

## Capture V0.1

Pour capturer automatiquement le trafic d'une simulation pendant une duree fixe :

```bash
sudo python3 src/carpet_bombing/characterization/capture_packets.py \
  --interface any \
  --duration 20 \
  --output src/carpet_bombing/simulations/simulation_v0.1/pcaps/capture_v0_1.pcap
```

Le script reste independant de la version de simulation : il suffit de changer le
chemin `--output` pour enregistrer la capture dans le dossier voulu.
