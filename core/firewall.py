import subprocess

SSH_PORT = 22

def run(cmd):
    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)

def setup_firewall(allowed_ips):
    """
    Safe firewall setup:
    - Keep SSH access
    - Allow established connections
    - Allow traffic only from allowed foreign IPs
    - Drop everything else
    """

    # Create custom chain to avoid flushing whole firewall
    run("iptables -N NET_ORCH 2>/dev/null")
    run("iptables -F NET_ORCH")

    # Allow established connections
    run(
        "iptables -A NET_ORCH "
        "-m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT"
    )

    # Allow SSH access (VERY IMPORTANT)
    run(
        f"iptables -A NET_ORCH "
        f"-p tcp --dport {SSH_PORT} -j ACCEPT"
    )

    # Allow traffic from known foreign servers
    for ip in allowed_ips:
        run(f"iptables -A NET_ORCH -s {ip} -j ACCEPT")

    # Drop everything else
    run("iptables -A NET_ORCH -j DROP")

    # Ensure INPUT chain sends traffic to NET_ORCH
    run(
        "iptables -C INPUT -j NET_ORCH 2>/dev/null || "
        "iptables -A INPUT -j NET_ORCH"
    )
