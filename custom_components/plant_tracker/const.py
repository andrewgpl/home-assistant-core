"""Constants for the Plant Tracker integration."""

from homeassistant.const import Platform

# Integration domain
DOMAIN = "plant_tracker"

# Supported platforms
PLATFORMS = [Platform.BUTTON, Platform.SENSOR]

# Config fields per plant
CONF_PLANT_ID = "plant_id"
CONF_NAME = "name"
CONF_PICTURE = "picture"

# Global options in YAML
CONF_PICTURES_PATH = "pictures_path"
CONF_DEFAULT_PICTURE = "default_picture"

# Attributes
ATTR_LAST_WATERED = "last_watered"
ATTR_LAST_FERTILIZED = "last_fertilized"
ATTR_DAYS_SINCE_WATERED = "days_since_watered"
ATTR_DAYS_SINCE_FERTILIZED = "days_since_fertilized"
ATTR_PICTURE = "picture"

# Default settings
DEFAULT_PICTURES_PATH = "/local/plant_tracker/pictures"
DEFAULT_PICTURE = "default_plant.png"
