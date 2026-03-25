from .const import DOMAIN

def get_store(hass):
    """Store for nodes and entities."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {
            "nodes": {},             # { node_name: {last_seen, status, value} }
            "entities": {},          # { node_name: XSensor instance }
            "discovered_nodes": {}   # { node_name: {host, port, data} }
        }
    return hass.data[DOMAIN]