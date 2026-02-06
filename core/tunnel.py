import subprocess

def run(cmd):
    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)

def setup_ipip(name, local, remote, private_ip):
    run("modprobe ipip")

    run(f"ip tunnel del {name}")
    run(
        f"ip tunnel add {name} mode ipip "
        f"local {local} remote {remote}"
    )
    run(f"ip link set {name} up")
    run(f"ip addr add {private_ip}/30 dev {name}")

    # allow IPIP traffic
    run("iptables -C INPUT -p 4 -j ACCEPT || iptables -A INPUT -p 4 -j ACCEPT")
