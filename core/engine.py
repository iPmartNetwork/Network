import json, time
from core.interface import detect_interface
from core.routing import add_route
from core.firewall import setup_firewall
from core.health import monitor

CONFIG = "config/profiles.json"

class Engine:
    def load_config(self):
        with open(CONFIG) as f:
            return json.load(f)

    def apply_profile(self, profile):
        iface = detect_interface()
        best = monitor(profile["foreign_servers"])

        if not best:
            print("All foreign servers DOWN")
            return

        add_route(best, profile["private_ip"], iface)
        setup_firewall(profile["foreign_servers"])
        print(f"Active FOREIGN server: {best}")

    def run_once(self):
        cfg = self.load_config()
        self.apply_profile(cfg)

    def run_daemon(self):
        while True:
            self.run_once()
            time.sleep(30)
