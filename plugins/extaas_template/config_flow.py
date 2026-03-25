from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """GUI kaudu Node lisamise vorm ja uue entry loomine"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Käsitle uue entry loomist."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input
            )

        # Vorm, mida kuvatakse kasutajale uue entry lisamisel
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("host"): str,
                vol.Optional("port", default=3000): int
            })
        )

    @staticmethod
    def async_get_options_flow(entry):
        """Tagastab OptionsFlow, et hiljem entry andmeid muuta."""
        return OptionsFlow(entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Entry andmete muutmine (IP, port, nimi)"""

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        """Kuva OptionsFlow vorm ja käsitle sisendit."""
        if user_input is not None:
            # uuenda entry andmeid
            self.entry.data.update(user_input)

            # uuenda olemasolevaid sensoreid, et muudatused peegelduks
            store = self.entry.hass.data.get(DOMAIN)
            if store and "sensors" in store:
                for sensor in store["sensors"].values():
                    if sensor.entry.entry_id == self.entry.entry_id:
                        # kirjutab uue state ja attributes HA-sse
                        sensor.async_write_ha_state()

            return self.async_create_entry(title="", data=user_input)

        data = self.entry.data

        # vorm, mis kuvab olemasolevad väärtused vaikimisi
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("name", default=data.get("name")): str,
                vol.Required("host", default=data.get("host")): str,
                vol.Optional("port", default=data.get("port", 3000)): int
            })
        )