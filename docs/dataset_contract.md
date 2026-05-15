# Contrat de dataset

Ce document définit le format commun de la dataset utilisée par les modules de
détection, de caractérisation et de mitigation.

L'objectif est que toute l'équipe travaille avec les mêmes fichiers, les mêmes
labels et les mêmes colonnes.

## Pourquoi ce document est important

Le projet produit plusieurs types de données :

- des captures réseau au format `.pcap` ou `.pcapng`
- des statistiques extraites depuis ces captures
- un fichier CSV final utilisable par les modules Python

Ce contrat sert de référence commune.

## Entrées

Les entrées sont les fichiers de capture réseau produits par la simulation.

Formats acceptés :

```text
.pcap
.pcapng
```

Emplacement recommandé :

```text
src/carpet_bombing/simulations/simulation_v0.1/pcaps/
```

## Sortie

La sortie principale est un fichier CSV contenant les caractéristiques extraites
des captures réseau.

Emplacement recommandé :

```text
src/carpet_bombing/simulations/simulation_v0.1/datasets/dataset_v0_1.csv
```

Ce fichier CSV pourra ensuite être utilisé pour :

- entraîner ou tester un module de détection
- analyser le comportement du trafic
- évaluer une stratégie de mitigation
- produire des graphiques et des statistiques

## Labels utilisés

Les labels servent à identifier le type de trafic présent dans une capture.

Labels recommandés :

```text
normal
ddos_single_target
carpet_udp
carpet_tcp_syn
carpet_icmp
carpet_mixed
attack
unknown
```

Signification :

- `normal` : trafic légitime
- `ddos_single_target` : attaque DDoS dirigée vers une seule adresse IP
- `carpet_udp` : attaque carpet bombing utilisant principalement UDP
- `carpet_tcp_syn` : attaque carpet bombing utilisant des paquets TCP SYN
- `carpet_icmp` : attaque carpet bombing utilisant ICMP
- `carpet_mixed` : attaque carpet bombing mélangeant plusieurs protocoles
- `attack` : attaque non précisée
- `unknown` : label impossible à déduire automatiquement

Si aucun label n'est donné au script d'extraction, le label est déduit depuis le
nom du fichier `.pcap`.

Exemples :

```text
normal_001.pcap                  -> normal
ddos_single_target_001.pcap      -> ddos_single_target
carpet_udp_001.pcap              -> carpet_udp
carpet_tcp_syn_001.pcap          -> carpet_tcp_syn
carpet_icmp_001.pcap             -> carpet_icmp
carpet_mixed_001.pcap            -> carpet_mixed
```

## Colonnes du CSV

Le CSV final doit contenir les colonnes suivantes :

```text
window_start
window_end
src_ip
dst_ip
protocol
src_port
dst_port
packet_count
byte_count
packets_per_second
bytes_per_second
unique_dst_count_for_src
is_dst_inactive
label
pcap_file
```

Description des colonnes :

- `window_start` : début de la fenêtre temporelle analysée
- `window_end` : fin de la fenêtre temporelle analysée
- `src_ip` : adresse IP source
- `dst_ip` : adresse IP destination
- `protocol` : protocole utilisé, par exemple TCP, UDP ou ICMP
- `src_port` : port source si disponible
- `dst_port` : port destination si disponible
- `packet_count` : nombre de paquets dans le flux
- `byte_count` : nombre total d'octets dans le flux
- `packets_per_second` : nombre de paquets par seconde
- `bytes_per_second` : nombre d'octets par seconde
- `unique_dst_count_for_src` : nombre de destinations différentes contactées par
  une même source dans la fenêtre temporelle
- `is_dst_inactive` : vaut `1` si la destination est considérée inactive, sinon
  `0`
- `label` : type de trafic
- `pcap_file` : nom du fichier de capture d'origine

## IP inactives

Par défaut, les IP considérées comme inactives sont :

```text
10.0.0.20-10.0.0.40
```

Ces adresses représentent des machines qui ne devraient normalement pas recevoir
de trafic.

Cette information est importante pour le carpet bombing, car une attaque peut
viser beaucoup d'adresses d'un même préfixe, y compris des adresses normalement
inactives.

## Utilisation du script d'extraction

Pour extraire les caractéristiques de tous les fichiers `.pcap` d'un dossier :

```bash
poetry run python src/carpet_bombing/characterization/extract_features.py \
  --input src/carpet_bombing/simulations/simulation_v0.1/pcaps \
  --output src/carpet_bombing/simulations/simulation_v0.1/datasets/dataset_v0_1.csv
```

Pour extraire un seul fichier avec un label imposé :

```bash
poetry run python src/carpet_bombing/characterization/extract_features.py \
  --input src/carpet_bombing/simulations/simulation_v0.1/pcaps/carpet_udp_001.pcap \
  --output src/carpet_bombing/simulations/simulation_v0.1/datasets/carpet_udp_001.csv \
  --label carpet_udp
```

Pour changer la plage d'IP inactives :

```bash
poetry run python src/carpet_bombing/characterization/extract_features.py \
  --input src/carpet_bombing/simulations/simulation_v0.1/pcaps \
  --output src/carpet_bombing/simulations/simulation_v0.1/datasets/dataset_v0_1.csv \
  --inactive-ranges 10.0.0.20-10.0.0.40
```

## Règle commune à respecter

Chaque nouveau scénario de simulation doit produire un fichier `.pcap` avec un
nom clair.

Exemples :

```text
normal_001.pcap
ddos_single_target_001.pcap
carpet_udp_001.pcap
carpet_tcp_syn_001.pcap
carpet_icmp_001.pcap
carpet_mixed_001.pcap
```

Le nom du fichier doit permettre de comprendre rapidement le type de trafic
capturé.
