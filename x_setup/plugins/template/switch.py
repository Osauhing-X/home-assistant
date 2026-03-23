"""Example switch entity for My Plugin 1"""

from homeassistant.components.switch import SwitchEntity

class MyPlugin1Switch(SwitchEntity):
    def __init__(self):
        self._is_on = False

    @property
    def name(self):
        return "My Plugin 1 Switch"

    @property
    def is_on(self):
        return self._is_on

    def turn_on(self, **kwargs):
        self._is_on = True
        # Tegevus Node.js serverile või muu logika

    def turn_off(self, **kwargs):
        self._is_on = False
        # Tegevus Node.js serverile või muu logika