"""Sensor entities for the Plant Tracker integration."""

from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    ATTR_DAYS_SINCE_FERTILIZED,
    ATTR_DAYS_SINCE_WATERED,
    ATTR_LAST_FERTILIZED,
    ATTR_LAST_WATERED,
    ATTR_PICTURE,
    DOMAIN,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Add sensor for a plant."""
    plant_id = entry.data["plant_id"]
    name = entry.data["name"]
    picture = entry.data.get("picture", None)

    sensor = PlantSensor(name, plant_id, picture)
    hass.data[DOMAIN][plant_id] = sensor
    async_add_entities([sensor])


class PlantSensor(RestoreEntity):
    """Sensor to track the state of a plant."""

    def __init__(self, name: str, plant_id: str, picture=None) -> None:
        """Initialize the PlantSensor entity."""
        self._name = name
        self._plant_id = plant_id
        self._picture = picture
        self._last_watered = None
        self._last_fertilized = None
        self._attr_name = f"{name} Sensor"
        self._attr_icon = "mdi:leaf"

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the sensor."""
        return f"plant_tracker_{self._plant_id}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the plant."""
        return "idle"

    @property
    def extra_state_attributes(self):
        """Return extra state attributes for the plant sensor."""
        attrs = {
            ATTR_LAST_WATERED: self._last_watered,
            ATTR_LAST_FERTILIZED: self._last_fertilized,
            ATTR_PICTURE: self._picture,
        }
        if self._last_watered:
            watered_time = datetime.fromisoformat(self._last_watered)
            attrs[ATTR_DAYS_SINCE_WATERED] = (datetime.now() - watered_time).days
        if self._last_fertilized:
            fertilized_time = datetime.fromisoformat(self._last_fertilized)
            attrs[ATTR_DAYS_SINCE_FERTILIZED] = (datetime.now() - fertilized_time).days

        return attrs

    async def async_added_to_hass(self):
        """Restore state when the sensor is added to Home Assistant."""
        state = await self.async_get_last_state()
        if state:
            self._last_watered = state.attributes.get(ATTR_LAST_WATERED)
            self._last_fertilized = state.attributes.get(ATTR_LAST_FERTILIZED)
            self._picture = state.attributes.get(ATTR_PICTURE)

    def water(self):
        """Mark the plant as watered."""
        self._last_watered = datetime.now().isoformat()
        self.schedule_update_ha_state()

    def fertilize(self):
        """Mark the plant as fertilized."""
        self._last_fertilized = datetime.now().isoformat()
        self.schedule_update_ha_state()

    def update_picture(self, picture_url):
        """Update the picture of the plant."""
        self._picture = picture_url
        self.schedule_update_ha_state()
