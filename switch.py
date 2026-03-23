from homeassistant.components.switch import SwitchEntity

class MySwitch(SwitchEntity):
    def __init__(self, name):
        self._name = name
        self._state = False

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        self._state = True

    async def async_turn_off(self, **kwargs):
        self._state = False

async def async_setup_entry(hass, entry, async_add_entities):
    entities = [MySwitch(f"Relay {i+1}") for i in range(3)]
    async_add_entities(entities)