#!/usr/bin/env python3

import socket
import sys
from concurrent.futures import ThreadPoolExecutor

open_ports = []

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

            print(f"[+] Port {port} OPEN ({service})")
            open_ports.append(port)

        s.close()

    except:
        pass


def load_ports(file):
    ports = []

    with open(file, "r") as f:
        for line in f:
            line = line.strip()

            if line.isdigit():
                ports.append(int(line))

    return ports


def main():

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <target-ip> <ports-file>")
        print(f"Example: {sys.argv[0]} 127.0.0.1 top-ports1000.txt")
        sys.exit(1)

    target = sys.argv[1]
    port_file = sys.argv[2]

    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print("[-] Invalid target")
        sys.exit(1)

    ports = load_ports(port_file)

    print(f"[*] Scanning {target_ip}")
    print(f"[*] Loaded {len(ports)} ports\n")

    with ThreadPoolExecutor(max_workers=100) as executor:
        for port in ports:
            executor.submit(scan_port, target_ip, port)

    print("\n[*] Scan Finished")

    if open_ports:
        print("[*] Open Ports:")
        for p in sorted(open_ports):
            print(f" - {p}")
    else:
        print("[-] No open ports found")


if __name__ == "__main__":
    main()
