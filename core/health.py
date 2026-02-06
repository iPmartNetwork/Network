import subprocess, time

def ping(ip):
    result = subprocess.run(
        ["ping", "-c", "2", ip],
        stdout=subprocess.DEVNULL
    )
    return result.returncode == 0

def monitor(servers):
    for s in servers:
        if ping(s):
            return s
    return None
