import time
from .const import DOMAIN

def format_unique_id(node: str) -> str:
    """Tagasta korrektne unique_id."""
    return f"x_{node.lower()}"

def get_device_info(node: str, config: dict):
    """Koosta device_info dictionary seadmete lehele."""
    return {
        "identifiers": {(DOMAIN, node)},
        "name": config.get("name", f"Extaas {node}"),
        "manufacturer": "Extaas",
        "model": "Node Client",
        "sw_version": f"Port {config.get('port', 3000)}",
    }

def update_last_seen(hass, node: str):
    """Uuenda viimase nägemise timestamp."""
    hass.data[DOMAIN]["last_seen"][node] = time.time()