import subprocess, ipaddress

def add_route(dest, via, dev):
    ipver = ipaddress.ip_address(dest).version
    if ipver == 4:
        cmd = f"ip route replace {dest} via {via} dev {dev}"
    else:
        cmd = f"ip -6 route replace {dest} via {via} dev {dev}"
    subprocess.run(cmd, shell=True)

def flush_routes(dev):
    subprocess.run(f"ip route flush dev {dev}", shell=True)
