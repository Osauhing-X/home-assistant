DOMAIN = "extaas_template"
SIGNAL_NEW_DATA = "extaas_template_update"

# ---------------------------
# HELPERS: ENTRY / DEVICE / ENTITY
# ---------------------------

def make_entry_id(hostname: str) -> str:
    """Entry ID (hostname/IP)"""
    return hostname.lower()

def make_entry_name(hostname: str) -> str:
    """Entry display name"""
    return hostname

def make_device_id(host: str, port: int) -> str:
    """Unique per host + port"""
    return f"{host}:{port}"

def make_device_name(service_name: str, port: int) -> str:
    """Device display name"""
    return f"{service_name} ({port})"

def make_entity_id(entry_id: str, device_id: str, name: str) -> str:
    """Unique ID per entity"""
    return f"{entry_id}:{device_id}:{name}"

def make_device_info(entry_id: str, host: str, port: int, service_name: str, icon: str = None):
    """Return HA device info dict"""
    return {
        "identifiers": {(DOMAIN, make_device_id(host, port))},
        "name": make_device_name(service_name, port),
        "manufacturer": "Extaas",
        "model": "Node Service",
        "via_device": None,
        "icon": icon,
    }