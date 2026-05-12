## Objectif du fichier

basic_topology.py permet de créer un petit réseau simulé via Mininet avec :

- 8 machines virtuelles légères : h1 à h8
- 1 switch virtuel : s1
- un réseau IP simple : 10.0.0.0/24

## C'est quoi Mininet ?

Mininet = un laboratoire réseau virtuel léger sur un ordinateur.

## Topologie actuelle

h1 ---|
h2 ---|
h3 ---|
h4 ---|--- s1
h5 ---|
h6 ---|
h7 ---|
h8 ---|

Tous les hôtes sont connectés au même switch virtuel s1.

Les adresses IP sont :

- h1 : 10.0.0.1/24
- h2 : 10.0.0.2/24
- h3 : 10.0.0.3/24
- h4 : 10.0.0.4/24
- h5 : 10.0.0.5/24
- h6 : 10.0.0.6/24
- h7 : 10.0.0.7/24
- h8 : 10.0.0.8/24

## Commande pour lancer la topologie

Depuis la racine du projet :

sudo python3 simulation/topology/basic_topology.py

Une console Mininet s'ouvre ensuite avec le prompt :

mininet>

## Commandes utiles dans Mininet

Afficher la topologie : net
Tester la connectivité entre tous les hôtes : pingall
Afficher l'adresse IP de h1 : h1 ip addr
Faire un ping de h1 vers h2 : h1 ping h2
Afficher les hôtes et switches disponibles : nodes
Quitter Mininet : exit

## Nettoyer Mininet après utilisation

sudo mn -c

## Résultat attendu

Avec cette topologie, la commande pingall doit afficher : 0% dropped
Cela signifie que tous les hôtes peuvent communiquer entre eux.
