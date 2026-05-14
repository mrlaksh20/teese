#!/usr/bin/env python3
import socket
import argparse
import re
from concurrent.futures import ThreadPoolExecutor

open_ports = []

def grab_banner(s, port):
    """Try to grab a banner or HTTP title from an open port."""
    banner = None
    try:
        # HTTP probe
        http_probe = f"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        s.sendall(http_probe.encode())
        response = s.recv(2048).decode(errors="ignore")

        # Try to extract HTML <title>
        title_match = re.search(r"<title>(.*?)</title>", response, re.IGNORECASE | re.DOTALL)
        if title_match:
            banner = f"Title: {title_match.group(1).strip()}"
        else:
            # Grab first non-empty line of HTTP response
            first_line = response.split("\n")[0].strip()
            if first_line:
                banner = f"HTTP: {first_line}"
    except:
        # Non-HTTP: try raw recv for banner (FTP, SSH, SMTP, etc.)
        try:
            raw = s.recv(1024).decode(errors="ignore").strip()
            if raw:
                banner = f"Banner: {raw.splitlines()[0][:120]}"
        except:
            pass
    return banner


def scan_port(target, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        result = s.connect_ex((target, port))
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"

            banner = grab_banner(s, port)
            banner_str = f" | {banner}" if banner else ""
            print(f"[+] {port}/tcp OPEN ({service}){banner_str}")
            open_ports.append((port, service, banner or ""))
        s.close()
    except:
        pass


def main():
    parser = argparse.ArgumentParser(description="Port Scanner with Banner Grabbing")
    parser.add_argument("target", help="Target IP or hostname")
    parser.add_argument("-p", "--ports", default="1-65535", help="Port range (default: 1-65535)")
    parser.add_argument("-t", "--threads", type=int, default=300, help="Number of threads (default: 300)")
    parser.add_argument("--timeout", type=float, default=1.0, help="Socket timeout in seconds (default: 1.0)")
    args = parser.parse_args()

    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print("[-] Invalid target")
        exit()

    # Parse port range
    ports = []
    for part in args.ports.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-")
                ports.extend(range(int(start), int(end) + 1))
            except:
                pass
        else:
            try:
                ports.append(int(part))
            except:
                pass

    ports = sorted(set(p for p in ports if 1 <= p <= 65535))

    print(f"[*] Target      : {target_ip}")
    print(f"[*] Total Ports : {len(ports)}")
    print(f"[*] Threads     : {args.threads}")
    print("[*] Scanning...\n")

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for port in ports:
            executor.submit(scan_port, target_ip, port)

    print("\n[*] Scan Complete")
    if open_ports:
        print(f"\n[*] {len(open_ports)} Open Port(s) Found:")
        print(f"{'PORT':<10} {'SERVICE':<15} {'BANNER/TITLE'}")
        print("-" * 70)
        for port, service, banner in sorted(open_ports):
            print(f"{port:<10} {service:<15} {banner}")
    else:
        print("[-] No open ports found")


if __name__ == "__main__":
    main()
