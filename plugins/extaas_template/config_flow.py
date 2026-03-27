from homeassistant import config_entries
import voluptuous as vol
from .options_flow import ExtaasOptionsFlowHandler
from .const import DOMAIN, DEFAULT_PORT

class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    # --- OPTIONS FLOW ---
    @staticmethod
    @config_entries.HANDLERS.register(DOMAIN)
    def async_get_options_flow(config_entry):
        """Return options flow handler."""
        return ExtaasOptionsFlowHandler(config_entry)


    # ---  MANUAL ---
    async def async_step_user(self, user_input=None):
        if user_input: # ON:SUBMIT
            return self.async_create_entry(
                title=user_input["hostname"],
                data=user_input )

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({
                vol.Required("hostname"): str,
                vol.Required("host"): str,
                vol.Optional("port", default=DEFAULT_PORT): int,
                vol.Required("service_name"): str }) )



    # --- AUTO ---
    async def async_step_zeroconf(self, discovery_info):
        # TXT OBJECT
        props_raw = discovery_info.properties or {}
        props = { # Helper (decode)
          (k.decode() if isinstance(k, bytes) else k):
          (v.decode() if isinstance(v, bytes) else v)
          for k, v in props_raw.items() }
        
        # VALUES
        hostname = discovery_info.hostname or props.get("node_name")
        host = props.get("hostname") or discovery_info.host
        port = discovery_info.port
        service_name = (props.get("service_name") or discovery_info.name).split("._")[0]


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
            "name": service_name or "X Device",
            "host": host or "Extaas",
            "port": port }


        """ REGISTER DEVICE """
        self._data = { # For async_step_confirm
            "hostname": hostname,
            "host": host,
            "port": port,
            "service_name": service_name }
        return await self.async_step_confirm()



    # --- CONFIRM ---
    async def async_step_confirm(self, user_input=None):
        if user_input: # ON:SUBMIT
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data["hostname"],  # Entry pealkiri = parent
                data=self._data )

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({
                vol.Required("service_name", default=self._data["service_name"]): str,
                vol.Required("host", default=self._data["host"]): str,
                vol.Required("port", default=self._data["port"]): int
            })
        )



    