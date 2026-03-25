import time
from .const import DOMAIN

def make_device_info(node, host, port):
    """Tagasta device_info objekt seadme kuvamiseks Devices lehel"""
    return {
        "identifiers": {(DOMAIN, node)},
        "name": node,
        "manufacturer": "Extaas",
        "model": "Node Client",
        "sw_version": f"Port {port}"
    }

def update_node_status(store, node, value=None, status="online"):
    """Uuenda node staatust ja last_seen"""
    store["connected"][node] = True
    store["value"][node] = value
    store["status"][node] = status
    store["last_seen"][node] = time.time()