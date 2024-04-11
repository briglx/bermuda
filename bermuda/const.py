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

LOW_TEMP = 60

MQTT_TOPIC = "monitor/blueleft/forecast/bermuda/growing"
MSG_TEMPLATE = "{{" + \
    "\"totalDaysAbove60Deg\":{}," + \
    "\"historicDaysAbove60Deg\":{}," + \
    "\"forcastDaysAbove60Deg\":{}" + \
    "}}"