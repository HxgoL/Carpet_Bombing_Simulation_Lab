# Module de mitigation

Ce module contient la partie mitigation du projet.

Son objectif est de recevoir une alerte ou un résultat de détection, puis de
préparer une action de mitigation adaptée.

## Rôle du module

Le module doit permettre de :

- recevoir un événement suspect
- décider quelle stratégie appliquer
- générer une action de mitigation
- appliquer cette action via un backend
- garder une trace de ce qui a été décidé

## Architecture

```text
mitigation/
├── models.py
├── policies.py
├── controller.py
├── config.py
├── strategies/
│   ├── prefix_rate_limit.py
│   ├── dynamic_filtering.py
│   ├── traffic_redistribution.py
│   └── traffic_classification.py
└── backends/
    ├── base.py
    └── dry_run.py
```

## Fichiers

- `models.py` : structures communes, comme les événements et les actions
- `policies.py` : politique adaptative qui choisit la meilleure stratégie
- `controller.py` : point d'entrée principal du module
- `config.py` : configuration par défaut
- `strategies/` : implémentation des familles de mitigation
- `backends/base.py` : interface commune pour appliquer une action
- `backends/dry_run.py` : backend de test qui n'applique aucune règle système

## Stratégies prévues

Le module est organisé autour de quatre familles demandées dans le sujet :

- limitation de débit par préfixe
- filtrage dynamique
- redistribution du trafic
- classification du trafic d'attaque

Pour garder un historique Git clair, les stratégies sont implémentées petit à
petit.

## Stratégie implémentée actuellement

La stratégie active actuellement est le filtrage dynamique.

Elle choisit une règle selon le type d'attaque identifié :

```text
carpet_udp      -> règle UDP
carpet_tcp_syn  -> règle TCP SYN
carpet_icmp     -> règle ICMP
```

Pour l'instant, le module génère seulement une prévisualisation de règle
`iptables`. Le backend par défaut reste `dry_run`.

## Principe de sécurité

Le backend par défaut est `dry_run`.

Il permet de tester les décisions de mitigation sans modifier la configuration
réseau de la machine.
