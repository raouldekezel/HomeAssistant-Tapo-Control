import voluptuous as vol
import logging
from datetime import timedelta
from homeassistant.helpers import config_validation as cv

DOMAIN = "tapo_control"
ALARM_MODE = "alarm_mode"
PRESET = "preset"
LIGHT = "light"
SOUND = "sound"
PRIVACY_MODE = "privacy_mode"
DAY_NIGHT_MODE = "day_night_mode"
LED_MODE = "led_mode"
NAME = "name"
DISTANCE = "distance"
TILT = "tilt"
PAN = "pan"
ENTITY_ID = "entity_id"
MOTION_DETECTION_MODE = "motion_detection_mode"
AUTO_TRACK_MODE = "auto_track_mode"
CLOUD_PASSWORD = "cloud_password"
DEFAULT_SCAN_INTERVAL = 10
SCAN_INTERVAL = timedelta(seconds=5)

ENABLE_MOTION_SENSOR = "enable_motion_sensor"

TOGGLE_STATES = ["on", "off"]

SERVICE_PTZ = "ptz"
SCHEMA_SERVICE_PTZ = {
    vol.Required(ENTITY_ID): cv.string,
    vol.Optional(TILT): vol.In(["UP", "DOWN"]),
    vol.Optional(PAN): vol.In(["RIGHT", "LEFT"]),
    vol.Optional(PRESET): cv.string,
    vol.Optional(DISTANCE): cv.string,
}

SERVICE_SET_PRIVACY_MODE = "set_privacy_mode"
SCHEMA_SERVICE_SET_PRIVACY_MODE = {
    vol.Required(ENTITY_ID): cv.string,
    vol.Required(PRIVACY_MODE): vol.In(TOGGLE_STATES),
}

SERVICE_SET_DAY_NIGHT_MODE = "set_day_night_mode"
SCHEMA_SERVICE_SET_DAY_NIGHT_MODE = {
    vol.Required(ENTITY_ID): cv.string,
    vol.Required(DAY_NIGHT_MODE): vol.In(["on", "off", "auto"]),
}

SERVICE_SET_ALARM_MODE = "set_alarm_mode"
SCHEMA_SERVICE_SET_ALARM_MODE = {
    vol.Required(ENTITY_ID): cv.string,
    vol.Required(ALARM_MODE): vol.In(TOGGLE_STATES),
    vol.Optional(SOUND): vol.In(TOGGLE_STATES),
    vol.Optional(LIGHT): vol.In(TOGGLE_STATES),
}

SERVICE_SET_LED_MODE = "set_led_mode"
SCHEMA_SERVICE_SET_LED_MODE = {
    vol.Required(ENTITY_ID): cv.string,
    vol.Required(LED_MODE): vol.In(TOGGLE_STATES),
}

SERVICE_SET_MOTION_DETECTION_MODE = "set_motion_detection_mode"
SCHEMA_SERVICE_SET_MOTION_DETECTION_MODE = {
    vol.Required(ENTITY_ID): cv.string,
    vol.Required(MOTION_DETECTION_MODE): vol.In(["high", "normal", "low", "off"]),
}

SERVICE_SET_AUTO_TRACK_MODE = "set_auto_track_mode"
SCHEMA_SERVICE_SET_AUTO_TRACK_MODE = {
    vol.Required(ENTITY_ID): cv.string,
    vol.Required(AUTO_TRACK_MODE): vol.In(TOGGLE_STATES),
}

SERVICE_REBOOT = "reboot"
SCHEMA_SERVICE_REBOOT = {vol.Required(ENTITY_ID): cv.string}

SERVICE_SAVE_PRESET = "save_preset"
SCHEMA_SERVICE_SAVE_PRESET = {
    vol.Required(ENTITY_ID): cv.string,
    vol.Required(NAME): cv.string,
}

SERVICE_DELETE_PRESET = "delete_preset"
SCHEMA_SERVICE_DELETE_PRESET = {
    vol.Required(ENTITY_ID): cv.string,
    vol.Required(PRESET): cv.string,
}

SERVICE_FORMAT = "format"
SCHEMA_SERVICE_FORMAT = {vol.Required(ENTITY_ID): cv.string}

ENABLE_STREAM = "enable_stream"

LOGGER = logging.getLogger("custom_components." + DOMAIN)
