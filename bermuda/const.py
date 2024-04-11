# coding: utf-8
"""Constants used by Bermuda."""
MAJOR_VERSION = 0
MINOR_VERSION = 1
PATCH_VERSION = '0.dev0'
__short_version__ = '{}.{}'.format(MAJOR_VERSION, MINOR_VERSION)
__version__ = '{}.{}'.format(__short_version__, PATCH_VERSION)
REQUIRED_PYTHON_VER = (3, 5, 3)

CONFIG_PATH = 'config.yaml'

CONF_MQTT_BROKER_ADDRESS = 'mqtt_broker_address'
CONF_MQTT_BROCKER_USERNAME = 'mqtt_broker_username'
CONF_MQTT_BROKER_PASSWORD = 'mqtt_broker_password'
CONF_MQTT_BROKER_PORT = 'mqtt_broker_port'

CONF_HOME_LATITUDE = 'home_latitude'
CONF_HOME_LONGITUDE = 'home_longitude'
CONF_DARKSKY_API_KEY = 'dark_sky_api_key'

ERR_TIMEOUT = "Fatal Error: Connection timeout for MQTT server {}."
ERR_CONFIG = "Fatal Error: Specified configuration files does not exist {}."

LOW_TEMP = 60
OVERSEED_DAYTIME_HIGH = 86
OVERSEED_DAYTIME_LOW = 79
OVERSEED_NIGHTIME_HIGH = 57
OVERSEED_NIGHTIME_LOW = 52

MQTT_GROWING_TOPIC = "monitor/blueleft/forecast/bermuda/growing"
MQTT_OVERSEED_TOPIC = "monitor/blueleft/forecast/bermuda/overseed"

MSG_GROWING_TEMPLATE = "{{" + \
    "\"totalDaysAbove60Deg\":{}," + \
    "\"historicDaysAbove60Deg\":{}," + \
    "\"forcastDaysAbove60Deg\":{}" + \
    "}}"
MSG_OVERSEED_TEMPLATE = "{{" + \
    "\"totalDaysIdealOverseeding\":{}" + \
    "}}"
