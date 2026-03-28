DOMAIN = "extaas_template"
SIGNAL_NEW_DATA = "extaas_template_update"

def make_device_id(host, port):
    return f"{host}:{port}"

def make_entity_id(entry_id, device_id, name):
    return f"{entry_id}:{device_id}:{name}"