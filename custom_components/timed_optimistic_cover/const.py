"""Constants for the Timed Optimistic Cover integration."""

from typing import Final

DOMAIN: Final = "timed_optimistic_cover"

CONF_COVER_ENTITY_ID: Final = "cover_entity_id"
CONF_HIDE_COVER_ENTITY: Final = "hide_cover_entity"
CONF_TIME_OPEN: Final = "time_open"
CONF_TIME_CLOSE: Final = "time_close"
CONF_SEND_STOP_AT_ENDS: Final = "send_stop_at_ends"
CONF_ALWAYS_CONFIDENT: Final = "always_confident"

DEFAULT_HIDE_COVER_ENTITY: Final = False
DEFAULT_TRAVEL_TIME: Final = 25
DEFAULT_SEND_STOP_AT_ENDS: Final = False
DEFAULT_ALWAYS_CONFIDENT: Final = False
