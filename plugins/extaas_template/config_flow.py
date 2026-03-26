# plugins/extaas_template/config_flow.py
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_zeroconf(self, discovery_info):
        """Handle zeroconf discovery."""
        props = discovery_info.properties or {}

        def get(key, default=None):
            val = props.get(key)
            if isinstance(val, bytes):
                return val.decode()
            return val or default

        host = discovery_info.host
        port = discovery_info.port

        node_name = get("node_name", discovery_info.name)
        service_name = get("service_name", "Unknown")

        # --- CUT after first ._ ---
        if "._" in node_name:
            node_name = node_name.split("._")[0]

        # --- UNIQUE PER IP ---
        await self.async_set_unique_id(host)

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        self._data = {
            "name": node_name,
            "host": host,
            "port": port
        }

        # Pealkiri = teenuse nimi, subpealkiri = IP
        self.context["title_placeholders"] = {
            "name": service_name,
            "host": host,
            "port": port
        }

        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        """Confirmation step."""
        if user_input:
            return self.async_create_entry(
                title=user_input["name"],
                data=self._data
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "host": self._data["host"]
            },
            data_schema=vol.Schema({
                vol.Required("name", default=self._data["name"]): str
            })
        )