"""Config flow for Timed Optimistic Cover integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.const import UnitOfTime
from homeassistant.components.cover import DOMAIN as COVER_DOMAIN

from homeassistant.helpers import selector
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)
from .const import (
    DOMAIN,
    CONF_COVER_ENTITY_ID,
    CONF_HIDE_COVER_ENTITY,
    CONF_TIME_OPEN,
    CONF_TIME_CLOSE,
    CONF_SEND_STOP_AT_ENDS,
    CONF_ALWAYS_CONFIDENT,
    DEFAULT_HIDE_COVER_ENTITY,
    DEFAULT_TRAVEL_TIME,
    DEFAULT_SEND_STOP_AT_ENDS,
    DEFAULT_ALWAYS_CONFIDENT,
)


TIME_SELECTOR = selector.NumberSelectorConfig(
    mode=selector.NumberSelectorMode.BOX,
    min=1,
    max=120,
    step="any",
    unit_of_measurement=UnitOfTime.SECONDS,
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_TIME_OPEN, default=DEFAULT_TRAVEL_TIME
        ): selector.NumberSelector(TIME_SELECTOR),
        vol.Required(
            CONF_TIME_CLOSE, default=DEFAULT_TRAVEL_TIME
        ): selector.NumberSelector(TIME_SELECTOR),
        vol.Required(
            CONF_SEND_STOP_AT_ENDS, default=DEFAULT_SEND_STOP_AT_ENDS
        ): selector.BooleanSelector(
            selector.BooleanSelectorConfig(),
        ),
        vol.Required(
            CONF_ALWAYS_CONFIDENT, default=DEFAULT_ALWAYS_CONFIDENT
        ): selector.BooleanSelector(
            selector.BooleanSelectorConfig(),
        ),
    }
)


CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_COVER_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=COVER_DOMAIN)
        ),
        vol.Required(
            CONF_HIDE_COVER_ENTITY, default=DEFAULT_HIDE_COVER_ENTITY
        ): selector.BooleanSelector(
            selector.BooleanSelectorConfig(),
        ),
    }
).extend(OPTIONS_SCHEMA.schema)

CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA)
}

OPTIONS_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(OPTIONS_SCHEMA)
}


class TimedOptimisticCoverConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config flow for Timed Optimistic Cover."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    VERSION = 1
    MINOR_VERSION = 1

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        registry = er.async_get(self.hass)

        name = options[CONF_COVER_ENTITY_ID]

        entity = registry.async_get(options[CONF_COVER_ENTITY_ID])
        if entity:
            if entity.name:
                name = entity.name
            if entity.original_name:
                name = entity.original_name

            if options[CONF_HIDE_COVER_ENTITY]:
                if not entity.hidden:
                    registry.async_update_entity(
                        options[CONF_COVER_ENTITY_ID],
                        hidden_by=er.RegistryEntryHider.INTEGRATION,
                    )

        return name
