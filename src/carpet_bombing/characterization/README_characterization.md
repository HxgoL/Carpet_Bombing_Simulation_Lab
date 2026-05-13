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
