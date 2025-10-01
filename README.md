# Timed Optimistic Cover

Add a timer to your simple, optimistic cover.

## Install

### HACS

Soon...

### Manually

1. Copy all files in [custom_components/timed_optimistic_cover](custom_components/timed_optimistic_cover) to your `<config directory>/custom_components/timed_optimistic_cover` directory.
2. Restart Home-Assistant

## Usage

[![Open your Home Assistant instance and add this integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=timed_optimistic_cover)

Or...

1. Go to Settings -> Devices & Services -> Add integration
2. Search for "Timed Optimistic Cover", select
3. Set the new timed cover's settings, then Submit, Finish

## Tips

### Cover from script, button or switch

Create a [Template Cover](https://www.home-assistant.io/integrations/template#cover), define Open, Close and Stop actions from your scripts, buttons or switches, then you can select it as an Optimistic Cover.

You can leave the `state` variable empty, as an empty string: `""`

## Credits

This integration is based on the following components:

- https://github.com/davidramosweb/home-assistant-custom-components-cover-time-based
- https://github.com/nagyrobi/home-assistant-custom-components-cover-rf-time-based
- https://github.com/duhow/hass-cover-time-based
