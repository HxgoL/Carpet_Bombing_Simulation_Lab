def cleanup_processes(attackers, victims):
    for victim in victims:
        victim.cmd("pkill -f normal_traffic.py")
        victim.cmd("pkill -f packet_receiver.py")

    for attacker in attackers:
        attacker.cmd("pkill -f fragmented_carpet_bombing.py")
