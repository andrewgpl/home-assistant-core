"""Initialize the Plant Tracker integration."""

import logging
import os

from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import CONF_NAME, CONF_PICTURE, CONF_PLANT_ID, DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Plant Tracker integration via YAML (not used in most cases)."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN in config:
        for plant_id, plant_conf in config[DOMAIN].get("plants", {}).items():
            hass.data[DOMAIN][plant_id] = plant_conf

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Plant Tracker from a config entry."""

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    plant_id = entry.data[CONF_PLANT_ID]
    hass.data[DOMAIN][plant_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a Plant Tracker config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class UploadPlantImageView(HomeAssistantView):
    """View for uploading a plant's image."""

    url = "/api/plant_tracker/upload_image"
    name = "api:plant_tracker:upload_image"

    async def post(self, request):
        """Handle file upload."""
        try:
            # Get the uploaded file from the request
            data = await request.post()
            file = data.get("file")

            # If no file provided, raise an error
            if not file:
                return self.json({"error": "No file provided."}, status=400)

            # Define the save path within the `www` folder
            save_path = os.path.join(
                request.app["hass"].config.path("www"), "images", file.filename
            )

            # Make sure the images directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save the file to disk
            with open(save_path, "wb") as f:
                f.write(file.file.read())

            # Return the URL to the uploaded image
            return self.json({"image_url": f"/local/images/{file.filename}"})

        except Exception as e:
            _LOGGER.error("Error uploading plant image: %s", e)
            return self.json({"error": "Failed to upload image."}, status=500)
