"""Plant Tracker options flow."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import CONF_PICTURE


class PlantTrackerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Plant Tracker options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.options = dict(config_entry.options)
        self.data = dict(config_entry.data)

    async def async_step_init(self, user_input=None) -> config_entries.ConfigFlowResult:
        """Manage Plant Tracker options."""
        if user_input is not None:
            if CONF_PICTURE in user_input and user_input[CONF_PICTURE] == "":
                user_input[CONF_PICTURE] = None

            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "picture",
                    default=self.options.get(
                        CONF_PICTURE, self.data.get(CONF_PICTURE, "")
                    )
                    or "",
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )
