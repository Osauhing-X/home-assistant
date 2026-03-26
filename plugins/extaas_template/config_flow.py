from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_zeroconf(self, discovery_info):
        props = discovery_info.properties or {}

        # Lihtne lõikamine ._extaas-node._tcp.local
        name = discovery_info.name.split("._")[0]  # "taavi-book-13"
        host = discovery_info.host
        port = discovery_info.port

        # Kasutame serverit, et näidata teenuse nime
        service_name = discovery_info.server or "Unknown"
        node_name = props.get("node_name", name)

        # UNIQUE ENTRY PER IP
        await self.async_set_unique_id(host)
        if self._async_current_entries():
            # Entry olemas → lihtsalt ignoreeri popup
            return self.async_abort(reason="already_configured")

        self._data = {
            "name": node_name,
            "host": host,
            "port": port,
            "service_name": service_name
        }

        # Zeroconf UI – title = teenuse nimi, subtitle = IP
        self.context["title_placeholders"] = {
            "name": service_name,   # title
            "host": host,           # subtitle
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

    async def async_step_user(self, user_input=None):
        if user_input:
            self._data = {
                "name": user_input["name"],
                "host": user_input["host"],
                "port": user_input["port"],
                "service_name": user_input.get("service_name", "Manual")
            }
            return self.async_create_entry(title=user_input["name"], data=self._data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("host"): str,
                vol.Required("port"): int
            })
        )