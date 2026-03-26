from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_zeroconf(self, discovery_info):
        props = discovery_info.properties or {}

        def get(key, default=None):
            val = props.get(key)
            return val.decode() if isinstance(val, bytes) else val or default

        host = discovery_info.host
        node_name = get("node_name", discovery_info.name)

        unique_id = host  # 🔥 ainult IP

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        self._data = {
            "name": node_name,
            "host": host
        }

        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        if user_input:
            return self.async_create_entry(
                title=user_input["name"],
                data=self._data
            )

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({
                vol.Required("name", default=self._data["name"]): str
            })
        )