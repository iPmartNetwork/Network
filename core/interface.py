import subprocess

def detect_interface():
    try:
        out = subprocess.check_output(
            "ip route get 1.1.1.1 | awk '{print $5}'",
            shell=True
        )
        return out.decode().strip()
    except:
        return "eth0"
