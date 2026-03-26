from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN


class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_zeroconf(self, discovery_info):
        props = discovery_info.properties or {}

        host = discovery_info.host
        port = discovery_info.port

        node_name = props.get("node_name") or discovery_info.name
        service_name = props.get("service_name") or "Unknown"

        # 👉 see määrab kuidas HA UI-s kuvatakse
        title = f"{service_name} ({host}:{port})"

        unique_id = f"{host}:{port}_{service_name}"

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        self._data = {
            "name": service_name,
            "node_name": node_name,
            "host": host,
            "port": port
        }

        return self.async_create_entry(
            title=title,
            data=self._data
        )

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("host"): str,
                vol.Required("port"): int
            })
        )