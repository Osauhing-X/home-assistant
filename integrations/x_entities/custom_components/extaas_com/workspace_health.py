"""Pure validation for the read-only Workspace connectivity check."""
import ipaddress
import re

def workspace_health_url(host, port):
    if not isinstance(host, str) or not host or len(host) > 253:
        raise ValueError("Invalid Workspace host")
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("Invalid Workspace port")
    try:
        address = ipaddress.ip_address(host)
        target = f"[{address}]" if address.version == 6 else str(address)
    except ValueError:
        if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,251}[A-Za-z0-9])?", host):
            raise ValueError("Invalid Workspace host") from None
        target = host.lower()
    return f"http://{target}:{port}/health"

def is_workspace_health(value):
    return isinstance(value, dict) and value.get("ok") is True and value.get("service") == "workspace-core"
