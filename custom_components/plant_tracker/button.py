"""Button entities for the Plant Tracker integration."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NAME, CONF_PLANT_ID, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the Plant Tracker integration."""

    plant_id = entry.data[CONF_PLANT_ID]
    name = entry.data[CONF_NAME]

    async_add_entities(
        [
            WaterPlantButton(name, plant_id, hass),
            FertilizePlantButton(name, plant_id, hass),
        ]
    )


class WaterPlantButton(ButtonEntity):
    """Button to manually water a plant."""

    def __init__(self, name: str, plant_id: str, hass: HomeAssistant) -> None:
        """Initialize WaterPlantButton entity."""
        self._attr_name = f"{name} - Water"
        self._attr_unique_id = f"plant_tracker_{plant_id}_water"
        self._attr_icon = "mdi:watering-can"
        self._plant_id = plant_id
        self._hass = hass

    async def async_press(self) -> None:
        """Handle the button press to water the plant."""
        sensor = self._hass.data[DOMAIN].get(self._plant_id)
        if sensor:
            sensor.water()


class FertilizePlantButton(ButtonEntity):
    """Button to manually fertilize a plant."""

    def __init__(self, name: str, plant_id: str, hass: HomeAssistant) -> None:
        """Initialize FertilizePlantButton entity."""
        self._attr_name = f"{name} - Fertilize"
        self._attr_unique_id = f"plant_tracker_{plant_id}_fertilize"
        self._attr_icon = "mdi:spray-bottle"
        self._plant_id = plant_id
        self._hass = hass

    async def async_press(self) -> None:
        """Handle the button press to fertilize the plant."""
        sensor = self._hass.data[DOMAIN].get(self._plant_id)
        if sensor:
            sensor.fertilize()
