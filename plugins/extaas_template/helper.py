import time
from .const import DOMAIN

def format_unique_id(node: str, key: str = None) -> str:
    if key:
        return f"x_{node.lower()}_{key.lower()}"
    return f"x_{node.lower()}"

def get_device_info(node: str, config: dict):
    return {
        "identifiers": {(DOMAIN, node)},
        "name": config.get("name", f"Extaas {node}"),
        "manufacturer": "Extaas",
        "model": "Node Client",
        "sw_version": f"Port {config.get('port', 3000)}",
    }

def update_last_seen(store, node: str):
    store["last_seen"][node] = time.time()