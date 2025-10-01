"""The Timed Optimistic Cover integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.cover import DOMAIN as COVER_DOMAIN
from homeassistant.helpers import entity_registry as er
import voluptuous as vol


from .const import (
    CONF_COVER_ENTITY_ID,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Timed Optimistic Cover from a config entry."""
    # TODO Optionally store an object for your platforms to access
    # entry.runtime_data = ...

    # TODO Optionally validate config entry options before setting up platform

    # await hass.config_entries.async_forward_entry_setups(entry, (Platform.COVER,))
    await hass.config_entries.async_forward_entry_setups(entry, (COVER_DOMAIN,))

    # TODO Remove if the integration does not have an options flow
    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))

    return True


# TODO Remove if the integration does not have an options flow
async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, (COVER_DOMAIN,))


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Unload a config entry.

    This will unhide the wrapped entity and restore assistant expose
    settings.
    """
    registry = er.async_get(hass)
    try:
        cover_entity_id = er.async_validate_entity_id(
            registry, entry.options[CONF_COVER_ENTITY_ID]
        )
    except vol.Invalid:
        # The source entity has been removed from the entity registry
        return

    if not (cover_entity := registry.async_get(cover_entity_id)):
        return

    # Unhide the wrapped entity
    if cover_entity.hidden_by == er.RegistryEntryHider.INTEGRATION:
        registry.async_update_entity(cover_entity_id, hidden_by=None)
