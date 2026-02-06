#!/usr/bin/env python3
import os, subprocess, sys

APT_PACKAGES = [
    "iproute2", "iptables", "nftables",
    "curl", "jq", "wireguard"
]

PIP_PACKAGES = ["rich", "psutil", "requests"]

def run(cmd):
    subprocess.run(cmd, shell=True, check=False)

def require_root():
    if os.geteuid() != 0:
        print("Run installer as root")
        sys.exit(1)

def install_apt():
    run("apt update")
    for p in APT_PACKAGES:
        run(f"apt install -y {p}")

def install_pip():
    run("apt install -y python3-pip")
    for p in PIP_PACKAGES:
        run(f"pip3 install {p}")

def enable_bbr():
    run("modprobe tcp_bbr")
    run("sysctl -w net.ipv4.tcp_congestion_control=bbr")
    run("sysctl -w net.core.default_qdisc=fq")

if __name__ == "__main__":
    require_root()
    install_apt()
    install_pip()
    enable_bbr()
    print("Installer finished successfully")
