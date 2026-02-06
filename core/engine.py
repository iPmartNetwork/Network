import os
import json
import time

from core.interface import detect_interface
from core.routing import add_route
from core.firewall import setup_firewall
from core.health import monitor
from core.geo import lookup

CONFIG_PATH = "config/profiles.json"

# ASN blacklist (penalty-based, NOT hard block)
BLACKLIST_ASN = {
    "AS13335",  # Cloudflare
    "AS16509",  # Amazon
    "AS15169",  # Google
}


class Engine:
    def __init__(self):
        self.last_active_foreign = None

    # -------------------------------------------------
    # Config handling
    # -------------------------------------------------
    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            print(f"[ERROR] profiles.json not found at {CONFIG_PATH}")
            return None

        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print("[ERROR] profiles.json is invalid JSON:", e)
            return None
        except Exception as e:
            print("[ERROR] Cannot read profiles.json:", e)
            return None

    # -------------------------------------------------
    # Geo-aware scoring
    # -------------------------------------------------
    def score_server(self, ip: str) -> int:
        """
        Lower score = better candidate
        """
        score = 0

        geo = lookup(ip)
        if not geo:
            print(f"[GEO] {ip}: geo lookup failed")
            return score + 10

        country = geo.get("country")
        asn = geo.get("asn")
        is_cdn = geo.get("is_cdn")

        print(
            f"[GEO] {ip}: country={country}, asn={asn}, cdn={is_cdn}"
        )

        # Warning only: Iran IP
        if country == "IR":
            print(f"[WARN] {ip} appears to be located in IRAN")
            score += 100

        # Penalize CDN usage
        if is_cdn:
            score += 50

        # Penalize blacklisted ASN
        if asn in BLACKLIST_ASN:
            score += 100

        return score

    # -------------------------------------------------
    # Server selection (Health + Geo)
    # -------------------------------------------------
    def select_best_server(self, servers):
        candidates = []

        for ip in servers:
            # Basic health check
            if not monitor([ip]):
                print(f"[HEALTH] {ip} is DOWN")
                continue

            score = self.score_server(ip)
            candidates.append((score, ip))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    # -------------------------------------------------
    # Apply profile
    # -------------------------------------------------
    def apply_profile(self, profile: dict):
        role = profile.get("role")
        if role != "IRAN":
            print("[INFO] Role is not IRAN, skipping orchestration")
            return

        foreign_servers = profile.get("foreign_servers", [])

        private_ip = (
            profile.get("network", {}).get("private_ip")
            or profile.get("private_ip")
        )

        firewall_enabled = profile.get("firewall", {}).get(
            "enabled",
            profile.get("firewall_enabled", False)
        )

        if not foreign_servers:
            print("[ERROR] No foreign_servers defined")
            return

        if not private_ip:
            print("[ERROR] private_ip is not defined")
            return

        interface = detect_interface()

        best_server = self.select_best_server(foreign_servers)
        if not best_server:
            print("[WARN] No healthy FOREIGN server available")
            return

        # Prevent unnecessary re-apply
        if best_server == self.last_active_foreign:
            return

        print(f"[DECISION] Selected FOREIGN server: {best_server}")
        print(f"[NET] Using interface: {interface}")

        # Apply routing
        add_route(best_server, private_ip, interface)

        # Apply firewall rules
        if firewall_enabled:
            setup_firewall(foreign_servers)

        self.last_active_foreign = best_server

    # -------------------------------------------------
    # Run modes
    # -------------------------------------------------
    def run_once(self):
        profile = self.load_config()
        if not profile:
            return
        self.apply_profile(profile)

    def run_daemon(self, interval: int = 30):
        print("[INFO] Net-Orchestrator started (Geo-Aware Engine)")
        while True:
            try:
                self.run_once()
            except Exception as e:
                print("[ERROR] Engine runtime error:", e)
            time.sleep(interval)
