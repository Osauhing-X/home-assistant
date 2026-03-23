import requests
from homeassistant.components.switch import SwitchEntity

class MySwitch(SwitchEntity):
    def __init__(self, name, id):
        self._name = name
        self._state = False
        self._id = id

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        self._state = True
        try:
            requests.post(f"http://<nodejs_ip>:3000/switch/{self._id}", json={"action": "on"})
        except:
            pass

    async def async_turn_off(self, **kwargs):
        self._state = False
        try:
            requests.post(f"http://<nodejs_ip>:3000/switch/{self._id}", json={"action": "off"})
        except:
            pass