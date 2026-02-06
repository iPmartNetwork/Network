"""
Net Orchestrator Core Package
Handles routing, firewall, health checks and decision engine
"""

__version__ = "0.1.0"

from .engine import Engine
from .interface import detect_interface
from .routing import add_route
from .firewall import setup_firewall
from .health import monitor

__all__ = [
    "Engine",
    "detect_interface",
    "add_route",
    "setup_firewall",
    "monitor"
]
