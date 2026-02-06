import os
import json
import time

from core.interface import detect_interface
from core.routing import add_route
from core.firewall import setup_firewall
from core.health import monitor

CONFIG_PATH = "config/profiles.json"


class Engine:
    def __init__(self):
        self.last_active_foreign = None

    # ---------------------------
    # Config handling
    # ---------------------------
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

    # ---------------------------
    # Core logic
    # ---------------------------
    def apply_profile(self, profile: dict):
        role = profile.get("role")
        foreign_servers = profile.get("foreign_servers", [])
        private_ip = profile.get("network", {}).get("private_ip") \
            or profile.get("private_ip")
        firewall_enabled = profile.get("firewall", {}).get(
            "enabled", profile.get("firewall_enabled", False)
        )

        if role != "IRAN":
            print("[INFO] Role is not IRAN, nothing to do")
            return

        if not foreign_servers:
            print("[ERROR] No foreign servers defined")
            return

        if not private_ip:
            print("[ERROR] private_ip is not defined")
            return

        # Detect interface
        interface = detect_interface()

        # Health check & failover
        active_foreign = monitor(foreign_servers)

        if not active_foreign:
            print("[WARN] All foreign servers are DOWN")
            return

        # Avoid re-applying same state
        if active_foreign == self.last_active_foreign:
            return

        print(f"[INFO] Active FOREIGN server selected: {active_foreign}")

        # Apply routing
        add_route(active_foreign, private_ip, interface)

        # Apply firewall rules if enabled
        if firewall_enabled:
            setup_firewall(foreign_servers)

        self.last_active_foreign = active_foreign

    # ---------------------------
    # Execution modes
    # ---------------------------
    def run_once(self):
        profile = self.load_config()
        if not profile:
            return
        self.apply_profile(profile)

    def run_daemon(self, interval: int = 30):
        print("[INFO] Net-Orchestrator daemon started")
        while True:
            try:
                self.run_once()
            except Exception as e:
                print("[ERROR] Engine runtime error:", e)
            time.sleep(interval)
