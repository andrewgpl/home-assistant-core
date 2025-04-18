"""Initialize the Plant Tracker integration."""

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_PICTURE,
    CONF_PICTURES_PATH,
    CONF_PLANT_ID,
    DEFAULT_PICTURE,
    DEFAULT_PICTURES_PATH,
    DOMAIN,
    PLATFORMS,
)
from .sensor import PlantSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Plant Tracker integration via YAML (not used in most cases)."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][CONF_PICTURES_PATH] = DEFAULT_PICTURES_PATH

    if DOMAIN in config:
        _LOGGER.debug("Loading Plant Tracker global settings from configuration.yaml")
        hass.data[DOMAIN].update(config[DOMAIN])

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Plant Tracker from a config entry."""

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    plant_id = entry.data[CONF_PLANT_ID]
    hass.data[DOMAIN][plant_id] = entry.data

    # Global options
    pictures_path = entry.options.get(CONF_PICTURES_PATH, DEFAULT_PICTURES_PATH)
    hass.data[DOMAIN][CONF_PICTURES_PATH] = pictures_path

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a Plant Tracker config entry and optionally delete image."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        picture_name = entry.options.get(CONF_PICTURE) or entry.data.get(CONF_PICTURE)
        if picture_name and picture_name != DEFAULT_PICTURE:
            pictures_path = entry.options.get(
                CONF_PICTURES_PATH, DEFAULT_PICTURES_PATH
            ).replace("/local/", "")
            full_path = Path(hass.config.path("www")) / pictures_path / picture_name

            if full_path.exists():
                try:
                    full_path.unlink()
                    _LOGGER.info("Deleted image for removed plant: %s", full_path)
                except OSError:
                    _LOGGER.exception(
                        "Failed to delete image for removed plant: %s", full_path
                    )

    return unload_ok


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle updated options for Plant Tracker."""
    plant_id = entry.data[CONF_PLANT_ID]
    sensor: PlantSensor = hass.data[DOMAIN].get(plant_id)

    if not sensor:
        return

    new_picture = entry.options.get(CONF_PICTURE, entry.data.get(CONF_PICTURE, ""))
    await sensor.async_update_picture(new_picture)
