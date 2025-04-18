"""Handle the options flow for the Plant Tracker integration."""

from __future__ import annotations

import logging
from pathlib import Path

import aiohttp
import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_PICTURE,
    CONF_PICTURES_PATH,
    CONF_PLANT_ID,
    DEFAULT_PICTURE,
    DEFAULT_PICTURES_PATH,
)

_LOGGER = logging.getLogger(__name__)


class PlantTrackerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the Plant Tracker options."""

    options: dict
    data: dict

    async def async_step_init(self, user_input=None) -> config_entries.ConfigFlowResult:
        """Handle the main options step."""
        self.options = dict(self.config_entry.options)
        self.data = dict(self.config_entry.data)

        return self.async_show_menu(
            step_id="init",
            menu_options={
                "edit_options": "Edit Plant Options",
                "upload_image": "Upload New Image",
            },
        )

    async def async_step_edit_options(self, user_input=None):
        """Edit picture options for the plant."""
        picture_current = self.options.get(CONF_PICTURE)
        if picture_current is None:
            picture_current = self.data.get(CONF_PICTURE) or ""

        if user_input is not None:
            clear_picture = user_input.get("clear_picture", False)
            picture_value = user_input.get(CONF_PICTURE, picture_current)
            if clear_picture:
                picture_value = ""

            _LOGGER.debug(
                "Picture update: old='%s', new='%s', clear=%s",
                picture_current,
                picture_value,
                clear_picture,
            )

            if (
                picture_current
                and picture_value == ""
                and picture_current != DEFAULT_PICTURE
            ):
                await self._remove_picture_file(picture_current)

            self.options[CONF_PICTURE] = picture_value

            self.hass.config_entries.async_update_entry(
                self.config_entry,
                options=self.options,
            )

            return self.async_abort(reason="options_updated")

        options_schema = vol.Schema(
            {
                vol.Optional(CONF_PICTURE, default=picture_current): str,
                vol.Optional("clear_picture", default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="edit_options",
            data_schema=options_schema,
        )

    async def async_step_upload_image(self, user_input=None):
        """Upload a new plant image."""
        if user_input is not None:
            image_url = user_input["image_url"]

            filename = await self._download_image(image_url)

            if filename:
                self.options[CONF_PICTURE] = filename

            self.hass.config_entries.async_update_entry(
                self.config_entry,
                options=self.options,
            )

            return self.async_abort(reason="options_updated")

        upload_schema = vol.Schema(
            {
                vol.Required("image_url"): str,
            }
        )

        return self.async_show_form(
            step_id="upload_image",
            data_schema=upload_schema,
        )

    async def _download_image(self, image_url: str) -> str | None:
        """Download and save plant image from URL."""
        _LOGGER.debug("Starting download of plant image from URL: %s", image_url)

        pictures_path = self.config_entry.options.get(
            CONF_PICTURES_PATH, DEFAULT_PICTURES_PATH
        ).replace("/local/", "")
        plant_id = self.config_entry.data.get(CONF_PLANT_ID)

        folder = Path(self.hass.config.path("www")) / pictures_path
        folder.mkdir(parents=True, exist_ok=True)

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(image_url) as response,
            ):
                if response.status != 200:
                    _LOGGER.error(
                        "Failed to download plant image, status code: %s",
                        response.status,
                    )
                    return None

                content_type = response.headers.get("Content-Type", "").lower()
                _LOGGER.debug("Content-Type received: %s", content_type)

                if "image/png" in content_type:
                    extension = "png"
                elif "image/jpeg" in content_type or "image/jpg" in content_type:
                    extension = "jpg"
                elif "image/webp" in content_type:
                    extension = "webp"
                elif "image/bmp" in content_type:
                    extension = "bmp"
                else:
                    _LOGGER.error("Unsupported image content type: %s", content_type)
                    return None

                file_data = await response.read()
                filename = f"{plant_id}.{extension}"
                full_path = folder / filename

                full_path.write_bytes(file_data)
                _LOGGER.info(
                    "Successfully downloaded and saved plant image as %s", filename
                )

                await self._clean_old_images(folder, plant_id, extension)

                return filename

        except aiohttp.ClientError:
            _LOGGER.exception("Failed to download plant image due to connection error")
            return None

    async def _clean_old_images(self, folder: Path, plant_id: str, new_extension: str):
        """Remove old images for the plant except the newly saved one."""
        try:
            for file in folder.iterdir():
                if file.name.startswith(f"{plant_id}.") and not file.name.endswith(
                    f".{new_extension}"
                ):
                    if file.is_file():
                        file.unlink()
                        _LOGGER.info("Removed outdated plant image: %s", file)
        except OSError:
            _LOGGER.exception("Failed to clean old images for %s", plant_id)

    async def _remove_picture_file(self, picture_name: str):
        """Remove a specific picture file."""
        pictures_path = self.config_entry.options.get(
            CONF_PICTURES_PATH, DEFAULT_PICTURES_PATH
        ).replace("/local/", "")
        full_path = Path(self.hass.config.path("www")) / pictures_path / picture_name

        if full_path.exists():
            try:
                full_path.unlink()
                _LOGGER.info(
                    "Deleted plant picture after user cleared it: %s", full_path
                )
            except OSError:
                _LOGGER.exception(
                    "Failed to delete cleared plant picture: %s", full_path
                )
