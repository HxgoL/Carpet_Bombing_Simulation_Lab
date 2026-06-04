import argparse
import ipaddress


def parse_ip_range(raw_range: str) -> list[str]:
    start_raw, end_raw = raw_range.split("-", maxsplit=1)
    start_ip = int(ipaddress.ip_address(start_raw.strip()))
    end_ip = int(ipaddress.ip_address(end_raw.strip()))

    if start_ip > end_ip:
        raise ValueError("Invalid range: start IP is greater than end IP")

    return [str(ipaddress.ip_address(value)) for value in range(start_ip, end_ip + 1)]


def parse_ip_list(raw_ips: str) -> list[str]:
    ips = [ip.strip() for ip in raw_ips.split(",") if ip.strip()]
    if not ips:
        raise ValueError("IP list cannot be empty")
    return [str(ipaddress.ip_address(ip)) for ip in ips]


def parse_sources(args: argparse.Namespace) -> list[str]:
    if args.src_ip:
        return [str(ipaddress.ip_address(args.src_ip.strip()))]
    if args.src_range:
        return parse_ip_range(args.src_range)
    return parse_ip_list(args.src_ips)


def parse_destinations(args: argparse.Namespace) -> list[str]:
    if args.dst_ip:
        return [str(ipaddress.ip_address(args.dst_ip.strip()))]
    return parse_ip_range(args.dst_range)
