from .const import DOMAIN

def get_store(hass):
    """Salvestab node info ja entity viited."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {
            "nodes": {},             # { node_name: {last_seen, heartbeat_data} }
            "entities": {},          # { node_name: {key_name: XSensor instance} }
            "discovered_nodes": {}   # { node_name: {host, port, last_data} }
        }
    return hass.data[DOMAIN]