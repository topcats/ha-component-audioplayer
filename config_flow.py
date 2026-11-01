from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    MIN_SCAN_INTERVAL_SECONDS,
    MAX_SCAN_INTERVAL_SECONDS,
)


def _config_schema(defaults: dict[str, object] | None = None) -> vol.Schema:
    """Build the setup/options form schema."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): vol.All(
                cv.string, vol.Length(min=1)
            ),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS
                ),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(
                    min=MIN_SCAN_INTERVAL_SECONDS,
                    max=MAX_SCAN_INTERVAL_SECONDS,
                ),
            ),
        }
    )


class TheOwlsAudioPlayerConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Handle setup of TheOwls AudioPlayer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, object] | None = None
    ) -> config_entries.FlowResult:
        """Show the initial configuration form."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="TheOwls RPI AudioPlayer",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_config_schema(),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> TheOwlsAudioPlayerOptionsFlow:
        """Return the options flow for an existing entry."""
        return TheOwlsAudioPlayerOptionsFlow(config_entry)


class TheOwlsAudioPlayerOptionsFlow(config_entries.OptionsFlow):
    """Handle AudioPlayer option changes."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, object] | None = None
    ) -> config_entries.FlowResult:
        """Show and save the options form."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_config_schema(
                {**self.config_entry.data, **self.config_entry.options}
            ),
        )
