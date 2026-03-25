import time
from .const import DOMAIN

def format_unique_id(node: str) -> str:
    return f"x_{node.lower()}"

def get_device_info(node: str, config: dict):
    return {
        "identifiers": {(DOMAIN, node)},
        "name": config.get("name", f"Extaas {node}"),
        "manufacturer": "Extaas",
        "model": "Node Client",
        "sw_version": f"Port {config.get('port', 3000)}",
    }

def update_last_seen(hass, node: str):
    hass.data[DOMAIN]["last_seen"][node] = time.time()