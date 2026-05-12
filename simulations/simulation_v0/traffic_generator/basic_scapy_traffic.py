from scapy.all import IP, ICMP, TCP, UDP, send

# Liste des hôtes cibles h2 à h8, h1 sert à envoyer les paquets
targets = [f"10.0.0.{i}" for i in range(2, 9)]

for target in targets:
    # Envoi de 3 paquets ICMP à chaque hôte
    send(IP(dst=target) / ICMP(), count=3, verbose=False)

    # Envoi de 5 paquets TCP SYN à chaque hôte vers le port HTTP 80
    send(IP(dst=target) / TCP(dport=80, flags="S"), count=5, verbose=False)

    # Envoi de 20 paquets UDP à chaque hôte vers le port DNS 53
    send(IP(dst=target) / UDP(dport=53), count=20, verbose=False)

print("Traffic generation completed")
