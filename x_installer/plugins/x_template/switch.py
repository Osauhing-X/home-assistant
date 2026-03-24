from homeassistant.components.switch import SwitchEntity

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([XTemplateSwitch()])

class XTemplateSwitch(SwitchEntity):
    def __init__(self):
        self._attr_name = "X Template Switch"
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs):
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs):
        self._attr_is_on = False