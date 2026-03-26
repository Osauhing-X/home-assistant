from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_zeroconf(self, discovery_info):
        props = discovery_info.properties or {}

        # lihtne lõikamine ._extaas-node._tcp.local
        name = discovery_info.name.split("._")[0]

        host = discovery_info.host
        port = discovery_info.port
        service_name = props.get("service_name", "Unknown")
        node_name = props.get("node_name", name)

        # UNIIKNE ENTRY PER IP
        await self.async_set_unique_id(host)
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        self._data = {
            "name": node_name,
            "host": host,
            "port": port,
            "service_name": service_name
        }

        # Zeroconf UI
        self.context["title_placeholders"] = {
            "name": service_name,
            "host": host,
            "port": port
        }

        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        if user_input:
            self._data["name"] = user_input["name"]
            return self.async_create_entry(title=user_input["name"], data=self._data)

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={"host": self._data["host"]},
            data_schema=vol.Schema({
                vol.Required("name", default=self._data["name"]): str
            })
        )