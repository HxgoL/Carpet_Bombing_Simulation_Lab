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
└── backends/
    ├── base.py
    └── dry_run.py
```

## Fichiers

- `models.py` : structures communes, comme les événements et les actions
- `policies.py` : stratégies de mitigation
- `controller.py` : point d'entrée principal du module
- `config.py` : configuration par défaut
- `backends/base.py` : interface commune pour appliquer une action
- `backends/dry_run.py` : backend de test qui n'applique aucune règle système

## Première stratégie

La première stratégie prévue est une limitation de débit au niveau du préfixe.

Exemple :

```text
Si une attaque carpet bombing est détectée sur 10.0.0.0/24,
le module prépare une règle de limitation de débit pour ce préfixe.
```

## Principe de sécurité

Le backend par défaut est `dry_run`.

Il permet de tester les décisions de mitigation sans modifier la configuration
réseau de la machine.
