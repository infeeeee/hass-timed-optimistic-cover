"""Cover support for Timed Optimistic Cover integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.cover import DOMAIN as COVER_DOMAIN
from homeassistant.components.cover import (
    ATTR_CURRENT_POSITION,
    CoverEntity,
    ATTR_POSITION,
)
from homeassistant.config_entries import ConfigEntry

from homeassistant.const import (
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
    SERVICE_STOP_COVER,
    STATE_UNAVAILABLE,
    ATTR_ASSUMED_STATE,
)
from homeassistant.core import callback, HomeAssistant

from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from homeassistant.util import slugify

from .const import (
    DOMAIN,
    CONF_COVER_ENTITY_ID,
    CONF_TIME_OPEN,
    CONF_TIME_CLOSE,
    CONF_SEND_STOP_AT_ENDS,
    CONF_ALWAYS_CONFIDENT,
)

from .travelcalculator import TravelCalculator

_LOGGER = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Initialize Timed Optimistic Cover config entry."""
    registry = er.async_get(hass)
    # Validate + resolve entity registry id to entity_id
    entity_id = er.async_validate_entity_id(
        registry, config_entry.options[CONF_COVER_ENTITY_ID]
    )
    cover_entity = registry.async_get(entity_id)

    cover_name = slugify(entity_id)
    cover_icon = None
    if cover_entity:
        _LOGGER.debug(f"cover_entity: {cover_entity}")
        if cover_entity.name:
            cover_name = cover_entity.name
        elif cover_entity.original_name:
            cover_name = cover_entity.original_name

        if cover_entity.icon:
            cover_icon = cover_entity.icon
        elif cover_entity.original_icon:
            cover_icon = cover_entity.original_icon

    _LOGGER.debug(f"config_entry: {config_entry}")

    async_add_entities(
        [
            TimedOptimisticCover(
                unique_id=config_entry.entry_id,
                cover_entity_id=entity_id,
                cover_name=cover_name,
                cover_icon=cover_icon,
                travel_time_up=config_entry.options.get(CONF_TIME_OPEN),
                travel_time_down=config_entry.options.get(CONF_TIME_CLOSE),
                send_stop_at_ends=config_entry.options.get(CONF_SEND_STOP_AT_ENDS),
                always_confident=config_entry.options.get(CONF_ALWAYS_CONFIDENT),
            )
        ]
    )


class TimedOptimisticCover(CoverEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_translation_key = DOMAIN

    def __init__(
        self,
        unique_id,
        cover_entity_id,
        cover_name,
        cover_icon,
        travel_time_up,
        travel_time_down,
        send_stop_at_ends,
        always_confident,
    ):
        """Initialize the cover."""
        self._cover_entity_id = cover_entity_id
        self._send_stop_at_ends = send_stop_at_ends

        self._attr_assumed_state = not always_confident
        self._attr_unique_id = unique_id
        self._attr_icon = cover_icon
        self._attr_translation_placeholders = {"cover_name": cover_name}

        self.tc = TravelCalculator(travel_time_up, travel_time_down)

        self._processing_known_position = False
        self._unsubscribe_auto_updater = None

    async def async_added_to_hass(self):
        """Only cover position and confidence in that matters."""
        """ The rest is calculated from this attribute.        """
        if not (old_state := await self.async_get_last_state()):
            return

        _LOGGER.debug(f"{self.name}: async_added_to_hass :: oldState: {old_state}")

        if old_state.attributes.get(ATTR_CURRENT_POSITION) is not None:
            self.tc.current_position = old_state.attributes.get(ATTR_CURRENT_POSITION)

    @property
    def available(self):
        state = self.hass.states.get(self._cover_entity_id)
        if state is None:
            return False
        if state.state == STATE_UNAVAILABLE:
            return False
        return True

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return {
            CONF_COVER_ENTITY_ID: str(self._cover_entity_id),
            CONF_TIME_OPEN: self.tc.travel_time_up,
            CONF_TIME_CLOSE: self.tc.travel_time_down,
            CONF_SEND_STOP_AT_ENDS: self._send_stop_at_ends,
            ATTR_ASSUMED_STATE: self._attr_assumed_state,
        }

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return self.tc.current_position

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""
        return bool(self.tc.direction > 0)

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""
        return bool(self.tc.direction < 0)

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return bool(self.current_cover_position == 0)

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        if ATTR_POSITION in kwargs:
            new_position = kwargs[ATTR_POSITION]

            await self.set_position(new_position)

    async def async_close_cover(self, **kwargs):
        """Turn the device close."""
        _LOGGER.debug(f"{self.name}: async_close_cover")
        await self.set_position(0)

    async def async_open_cover(self, **kwargs):
        """Turn the device open."""
        _LOGGER.debug(f"{self.name}: async_open_cover")
        await self.set_position(100)

    async def async_stop_cover(self, **kwargs):
        """Turn the device stop."""
        _LOGGER.debug(f"{self.name}: async_stop_cover")
        if self.tc.direction != 0:
            self.stop_auto_updater()
            self.tc.stop_travel()
            await self._async_handle_command(SERVICE_STOP_COVER)

    async def set_position(self, position):
        _LOGGER.debug(f"{self.name}: set_position: {position}")
        """Move cover to a designated position."""

        if self.tc.get_relative_direction(position) == 0:
            return

        command = (
            SERVICE_CLOSE_COVER
            if self.tc.get_relative_direction(position) < 0
            else SERVICE_OPEN_COVER
        )
        self.start_auto_updater()

        self.tc.set_position(position)
        await self._async_handle_command(command)

    def start_auto_updater(self):
        """Start the autoupdater to update HASS while cover is moving."""
        _LOGGER.debug(f"{self.name}: start_auto_updater")
        if self._unsubscribe_auto_updater is None:
            _LOGGER.debug(f"{self.name}: init _unsubscribe_auto_updater")
            interval = timedelta(seconds=0.1)
            self._unsubscribe_auto_updater = async_track_time_interval(
                self.hass, self.auto_updater_hook, interval
            )

    @callback
    def auto_updater_hook(self, now):
        """Call for the autoupdater."""
        _LOGGER.debug(
            f"{self.name}: auto_updater_hook, pos: {self.tc.current_position}"
        )
        self.async_schedule_update_ha_state()

        if self.tc.position_reached:
            _LOGGER.debug(f"{self.name}: auto_updater_hook :: position_reached")
            self.stop_auto_updater()
            if self.tc.current_position in [100, 1]:
                if not self._send_stop_at_ends:
                    return
            self.hass.async_create_task(self._async_handle_command(SERVICE_STOP_COVER))

    def stop_auto_updater(self):
        """Stop the autoupdater."""
        _LOGGER.debug(f"{self.name}: stop_auto_updater")
        if self._unsubscribe_auto_updater is not None:
            self._unsubscribe_auto_updater()
            self._unsubscribe_auto_updater = None

    async def _async_handle_command(self, command, *args):
        """We have cover.* triggered command. Reset assumed state and known_position processsing and execute"""

        await self.hass.services.async_call(
            COVER_DOMAIN, command, {"entity_id": self._cover_entity_id}
        )

        _LOGGER.debug(f"{self.name}: _async_handle_command :: {command}")

        # Update state of entity
        self.async_write_ha_state()
