"""Config flow for EV Charge Splitter integration."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN,
    CONF_CHARGER_POWER_SENSOR,
    CONF_GRID_IMPORT_SENSOR,
    CONF_BATTERY_DISCHARGE_SENSOR,
)


class EVChargeSplitterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EV Charge Splitter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Create the entry
            return self.async_create_entry(
                title="EV Charge Splitter",
                data=user_input,
            )

        # Show the form with dropdown selectors for sensors
        data_schema = vol.Schema(
            {
                vol.Required(CONF_CHARGER_POWER_SENSOR): selector(
                    {"entity": {"domain": "sensor"}}
                ),
                vol.Required(CONF_GRID_IMPORT_SENSOR): selector(
                    {"entity": {"domain": "sensor"}}
                ),
                vol.Required(CONF_BATTERY_DISCHARGE_SENSOR): selector(
                    {"entity": {"domain": "sensor"}}
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
