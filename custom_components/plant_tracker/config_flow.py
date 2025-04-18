"""Config flow for the Plant Tracker integration."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_NAME, CONF_PICTURE, CONF_PLANT_ID, DOMAIN
from .options_flow import PlantTrackerOptionsFlowHandler


class PlantTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plant Tracker."""

    VERSION = 1

    async def async_step_user(self, user_input=dict | None):
        """Handle the initial step of the user config flow."""

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_PLANT_ID: user_input[CONF_PLANT_ID],
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_PICTURE: user_input.get(CONF_PICTURE, ""),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PLANT_ID): str,
                    vol.Required(CONF_NAME): str,
                    vol.Optional(CONF_PICTURE): str,  # URL or local path
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> PlantTrackerOptionsFlowHandler:
        """Get the options flow."""
        return PlantTrackerOptionsFlowHandler()
