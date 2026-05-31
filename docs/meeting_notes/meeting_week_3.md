# Réunion Semaine 3

## Contexte discuté

- Une attaque venant d'Internet traverse généralement plusieurs routeurs entre la source et la destination.
- Exemple mentionné comme ordre de grandeur : une communication Canada-France ou ETS-France peut passer par environ 16 à 20 routeurs.
- À chaque routeur traversé, le TTL est décrémenté.
- Dans notre simulation locale, ce comportement n'est pas naturellement représenté si les paquets ne traversent pas plusieurs routeurs simulés ou réels.
- Pour se rapprocher d'un comportement plus réaliste, plusieurs pistes ont été évoquées :
  - utiliser une topologie multi-routeurs ;
  - utiliser GNS ou Packet Tracer ;
  - étudier FRRouting ;
  - simuler du routage dynamique avec des protocoles utilisés sur Internet ;
  - étudier des notions comme BGP entre domaines.
- Il a aussi été rappelé que ce qui nous intéresse surtout pour la détection est ce qui est observable dans les paquets : adresses sources, adresses destinations, TTL, taille, fragmentation, ports, protocoles et flags.

## Points techniques importants

- Le TTL peut être une feature intéressante, mais il doit être interprété avec prudence, car il dépend aussi du TTL initial choisi par la machine source.
- Les attaques peuvent venir de plusieurs machines ou sembler venir de plusieurs sources, notamment dans le cas d'IP usurpées ou distribuées.
- Les adresses IP sources peuvent varier dans certains scénarios d'attaque.
- Une piste évoquée est de changer l'adresse IP source simulée toutes les quelques secondes, uniquement dans un environnement contrôlé.
- Les attaques de type DNS amplification peuvent produire de grands paquets UDP et parfois de la fragmentation.
- La fragmentation doit donc être observée et analysée par l'analyseur de trafic.
- Une attaque carpet bombing vise un préfixe ou un lien, pas seulement une machine précise.
- L'objectif est d'avoir une machine ou un point de collecte qui observe ce qui arrive sur le sous-réseau cible.
- Le collecteur peut être placé côté réseau victime, par exemple à l'entrée du sous-réseau.
- Pour la mitigation, un IDS ou un firewall pourrait être placé avant ou après le routeur d'entrée du réseau victime.
- Ce qui se passe avant, dans Internet, n'est pas contrôlable par l'entreprise victime.
- Le trafic vers des IP inactives ou inexistantes du `/24` peut être considéré comme suspect.
- Le trafic vers des services non disponibles peut aussi être considéré comme suspect.
- Exemples de comportements suspects :
  - paquets vers des IP qui n'existent pas ;
  - SYN vers des machines clientes ;
  - trafic vers des services absents comme FTP, mail ou DNS ;
  - requêtes vers un service non disponible ;
  - attaque vers un `/24` alors que seulement une partie des adresses existe réellement ;
  - trafic anormalement dispersé sur un préfixe.
- Pour une attaque de type DNS amplification, certains comportements peuvent être tagués comme suspects, par exemple des réponses UDP volumineuses, fragmentées ou incohérentes avec les services disponibles.
- Il faut réfléchir à la détection et à la mitigation à partir de ces observations.

## Pistes avancées

- Simuler une architecture plus proche d'Internet avec plusieurs routeurs, si cela apporte des features observables utiles.
- Étudier FRRouting pour simuler des protocoles de routage dynamiques, sans en faire un objectif prioritaire immédiat.
- Étudier GNS ou Packet Tracer si Mininet devient trop limité pour représenter la topologie.
- Comparer une simulation locale avec des observations réelles autorisées, par exemple avec `traceroute`, pour comprendre les TTL.
- Ne pas générer d'attaque vers Internet sans autorisation : les comportements réalistes doivent d'abord être reproduits en laboratoire.

## Prochaines étapes réalistes

- Finaliser l'environnement de simulation actuel avant de partir sur une architecture Internet complète.
- Ajouter dans la génération de trafic :
  - TTL ;
  - fragmentation ;
  - variation des IP sources simulées ;
  - variation des destinations ;
  - ports et services ciblés.
- Définir les services réellement disponibles sur les machines victimes.
- Définir les machines clientes et les machines serveurs.
- Ajouter des règles de suspicion par paquet ou par flux :
  - destination inactive ;
  - service inexistant ;
  - SYN vers client simple ;
  - fragmentation ;
  - TTL inhabituel ;
  - dispersion sur le préfixe.
- Analyser ces nouveaux indicateurs avec l'analyseur de trafic.
- Réfléchir à la détection et à la mitigation à partir de ces nouvelles features.
