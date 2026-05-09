#!/usr/bin/env python3

import socket
import argparse
from concurrent.futures import ThreadPoolExecutor

open_ports = []


def parse_ports(port_string):
    ports = set()

    parts = port_string.split(",")

    for part in parts:
        part = part.strip()

        # Range like 20-25
        if "-" in part:
            try:
                start, end = part.split("-")

                start = int(start)
                end = int(end)

                for p in range(start, end + 1):
                    if 1 <= p <= 65535:
                        ports.add(p)

            except:
                pass

        # Single port
        else:
            try:
                p = int(part)

                if 1 <= p <= 65535:
                    ports.add(p)

            except:
                pass

    return sorted(ports)


def load_ports_from_file(filename):
    try:
        with open(filename, "r") as f:
            content = f.read().replace("\n", ",")

        return parse_ports(content)

    except FileNotFoundError:
        print("[-] Port file not found")
        exit()


def scan_port(target, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)

        result = s.connect_ex((target, port))

        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"

            print(f"[+] {port}/tcp OPEN ({service})")
            open_ports.append(port)

        s.close()

    except:
        pass


def main():

    parser = argparse.ArgumentParser(
        description="Mini Python Port Scanner"
    )

    parser.add_argument("target", help="Target IP or domain")
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Port file"
    )

    args = parser.parse_args()

    try:
        target_ip = socket.gethostbyname(args.target)

    except socket.gaierror:
        print("[-] Invalid target")
        exit()

    ports = load_ports_from_file(args.file)

    print(f"[*] Target      : {target_ip}")
    print(f"[*] Total Ports : {len(ports)}")
    print("[*] Scanning...\n")

    with ThreadPoolExecutor(max_workers=200) as executor:
        for port in ports:
            executor.submit(scan_port, target_ip, port)

    print("\n[*] Scan Finished")

    if open_ports:
        print("\n[*] Open Ports:")
        for port in sorted(open_ports):
            print(f" - {port}")
    else:
        print("[-] No open ports found")


if __name__ == "__main__":
    main()
