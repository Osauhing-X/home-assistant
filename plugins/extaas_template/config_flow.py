from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, DEFAULT_PORT

class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    # ---  MANUAL ---
    async def async_step_user(self, user_input=None):
        if user_input: # ON:SUBMIT
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input )

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("host"): str,
                vol.Optional("port", default=3000): int }) )



    # --- AUTO ---
    async def async_step_zeroconf(self, discovery_info):

        # TXT OBJECT
        props_raw = discovery_info.properties or {}
        props = { # Helper (decode)
          (k.decode() if isinstance(k, bytes) else k):
          (v.decode() if isinstance(v, bytes) else v)
          for k, v in props_raw.items() }
        
        # VALUES
        port = discovery_info.port
        hostname = discovery_info.hostname or props.get("node_name")
        host = props.get("hostname") or discovery_info.host
        name = (props.get("service_name") or discovery_info.name).split("._")[0]


        """ IS UNIQUE ?? 2FA """
        # 1️⃣ IP:PORT ?
        for entry in self._async_current_entries():
            if entry.data.get("host") == host and entry.data.get("port") == port:
                self.async_abort(reason="already_configured")
        
        # 2️⃣ NAME:PORT
        unique_id = f"{hostname.lower().replace(' ', '_')}:{port}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()


        """ AUTO DISCOVERY """
        self.context["title_placeholders"] = {
            "name": name or "Unknown",
            "host": host or "Extaas",
            "port": port }


        """ REGISTER DEVICE """
        self._data = { # For async_step_confirm
            "hostname": hostname,
            "name": name,
            "host": host,
            "port": port or DEFAULT_PORT }
        return await self.async_step_confirm()



    # --- CONFIRM ---
    async def async_step_confirm(self, user_input=None):
        if user_input: # ON:SUBMIT
            self._data.update({
                "name": user_input["name"],
                "host": user_input["host"],
                "port": user_input["port"] })
            return self.async_create_entry(
                title=self._data["name"],
                data=self._data )

        # Määrame step_title, mis kuvatakse vormi ülaosas
        self.context["step_title"] = f"Connecting to {self._data['hostname']}"

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({
                vol.Required("name", default=self._data["name"]): str,
                vol.Required("host", default=self._data["host"]): str,
                vol.Required("port", default=self._data["port"]): int
            })
        )



    