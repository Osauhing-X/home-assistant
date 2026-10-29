"""Runs inside the official HA image, with synthetic data and no network."""
import asyncio
import importlib
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0, "/config")
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntries
from custom_components.extaas_com import api, config_flow
for name in ("coordinator", "sensor", "binary_sensor", "switch", "button", "update"):
    importlib.import_module("custom_components.extaas_com." + name)
assert api.ExtaasApiView.requires_auth is True
async def main():
    with tempfile.TemporaryDirectory(prefix="workspace-ha-acceptance-") as root:
        hass = HomeAssistant(root)
        hass.config_entries = ConfigEntries(hass, {})
        flow = config_flow.ExtaasConfigFlow()
        flow.hass = hass
        flow.handler = "extaas_com"
        flow.context = {"source": "user"}
        form = await flow.async_step_user()
        assert form["type"] == "form" and form["step_id"] == "user"
        bad = await flow.async_step_user({"service_name": "Synthetic Workspace", "host": "http://bad/path", "port": 3010, "protocol": "workspace-core"})
        assert bad["errors"]["base"] == "cannot_connect"
        class Body:
            async def read(self, maximum):
                return b'{"ok":true,"service":"workspace-core"}'
        class Response:
            status = 200
            content = Body()
            async def __aenter__(self): return self
            async def __aexit__(self, *_): return False
        class Session:
            def get(self, url, **kwargs):
                assert url == "http://127.0.0.1:3010/health"
                assert kwargs["allow_redirects"] is False
                return Response()
        with patch.object(config_flow, "async_get_clientsession", return_value=Session()):
            result = await flow.async_step_user({"service_name": "Synthetic Workspace", "host": "127.0.0.1", "port": 3010, "protocol": "workspace-core"})
        assert result["type"] == "create_entry"
        assert result["data"]["protocol"] == "workspace-core"
        await hass.async_stop()
    print("Native HA imports, authenticated publishing and synthetic Core setup flow accepted.")
asyncio.run(main())
