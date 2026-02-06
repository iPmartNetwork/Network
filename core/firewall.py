import subprocess

def setup_firewall(allowed_ips):
    subprocess.run("iptables -F", shell=True)

    subprocess.run(
        "iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT",
        shell=True
    )

    for ip in allowed_ips:
        subprocess.run(
            f"iptables -A INPUT -s {ip} -j ACCEPT",
            shell=True
        )

    subprocess.run("iptables -A INPUT -j DROP", shell=True)
