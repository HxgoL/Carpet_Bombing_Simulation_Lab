import argparse
import socket
import threading
import time


def parse_args():
    parser = argparse.ArgumentParser(description="Simple packet receiver for V5 victims.")
    parser.add_argument("--udp-ports", nargs="+", type=int, default=[53, 123, 5000])
    parser.add_argument("--tcp-ports", nargs="+", type=int, default=[80, 443, 8080])
    return parser.parse_args()


def run_udp_sink(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))

    while True:
        sock.recvfrom(65535)


def run_tcp_sink(port):
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
        threading.Thread(target=run_udp_sink, args=(port,), daemon=True).start()

    for port in args.tcp_ports:
        threading.Thread(target=run_tcp_sink, args=(port,), daemon=True).start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    run()
