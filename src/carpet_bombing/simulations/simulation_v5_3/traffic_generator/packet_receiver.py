import argparse
import socket
import threading
import time


UDP_PORTS = [53, 123, 5000, 5353]
TCP_PORTS = [80, 443, 8080]


def parse_args():
    parser = argparse.ArgumentParser(description="Simple TCP/UDP receiver for V5.3 victims.")
    parser.add_argument("--udp-ports", nargs="+", type=int, default=UDP_PORTS)
    parser.add_argument("--tcp-ports", nargs="+", type=int, default=TCP_PORTS)
    return parser.parse_args()


def create_udp_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    return sock


def create_tcp_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    sock.listen(64)
    return sock


def run_udp_receiver(port):
    sock = create_udp_socket(port)
    while True:
        sock.recvfrom(65535)


def run_tcp_receiver(port):
    sock = create_tcp_socket(port)
    while True:
        conn, _addr = sock.accept()
        conn.close()


def start_daemon(target, port):
    thread = threading.Thread(target=target, args=(port,), daemon=True)
    thread.start()
    return thread


def run():
    args = parse_args()

    for port in args.udp_ports:
        start_daemon(run_udp_receiver, port)

    for port in args.tcp_ports:
        start_daemon(run_tcp_receiver, port)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    run()
