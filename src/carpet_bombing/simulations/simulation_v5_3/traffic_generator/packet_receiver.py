import argparse
import socket
import threading
import time

UDP_PORTS = [53, 123, 5000, 5353]
TCP_PORTS = [80, 443, 8080]

def parse_args():
    parser = argparse.ArgumentParser(description="Simple TCP/UDP receiver for V5 victims.")
    parser.add_argument("--udp-ports", nargs="+", type=int, default=UDP_PORTS)
    parser.add_argument("--tcp-ports", nargs="+", type=int, default=TCP_PORTS)
    return parser.parse_args()

def run_udp_receiver(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    while True:
        sock.recvfrom(65535)

def run_tcp_receiver(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    sock.listen(64)
    while True:
        conn, _addr = sock.accept()
        conn.close()

def run():
    args = parse_args()
    for port in args.udp_ports:
        threading.Thread(target=run_udp_receiver, args=(port,), daemon=True).start()
    for port in args.tcp_ports:
        threading.Thread(target=run_tcp_receiver, args=(port,), daemon=True).start()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    run()
