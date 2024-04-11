#!/usr/bin/env python3
"""Bermuda Growing Day script."""

from datetime import datetime, timedelta
import forecastio
import paho.mqtt.client as mqtt
import yaml
from bermuda import const as berm_const
import sys
import os


def ensure_config_path():
    """Check if config file exists"""
    if not os.path.isfile(berm_const.CONFIG_PATH):
        print((berm_const.ERR_CONFIG).format(berm_const.CONFIG_PATH))
        sys.exit(1)


def get_config():
    """Get configuration."""
    with open(berm_const.CONFIG_PATH, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    return cfg


def get_days(conf, historic=False):
    """Get number of day."""
    cur_time = datetime.utcnow()
    cur_time = cur_time.replace(minute=0, second=0, microsecond=0)
    last_week = cur_time - timedelta(days=7)

    if historic:
        forecast = forecastio.load_forecast(
            conf[berm_const.CONF_DARKSKY_API_KEY],
            conf[berm_const.CONF_HOME_LATITUDE],
            conf[berm_const.CONF_HOME_LONGITUDE],
            time=last_week
            )
    else:
        forecast = forecastio.load_forecast(
            conf[berm_const.CONF_DARKSKY_API_KEY],
            conf[berm_const.CONF_HOME_LATITUDE],
            conf[berm_const.CONF_HOME_LONGITUDE]
            )

    daily = forecast.daily()

    days_over_low = 0
    for data in daily.data:
        if data.apparentTemperatureLow > berm_const.LOW_TEMP:
            days_over_low += 1

    return days_over_low


def publish_growing_days(conf):
    """Publish the number of growing days to the mqtt broker."""
    try:
        # Connect to Mqqt broker
        mqtt_client = mqtt.Client()
        mqtt_client.username_pw_set(
            conf[berm_const.CONF_MQTT_BROCKER_USERNAME],
            conf[berm_const.CONF_MQTT_BROKER_PASSWORD]
            )
        mqtt_client.connect(
            conf[berm_const.CONF_MQTT_BROKER_ADDRESS],
            conf[berm_const.CONF_MQTT_BROKER_PORT]
            )

        # Get Forecast Count
        forecast_days_over_low = get_days(conf)

        # Get historic count
        historic_days_over_low = get_days(conf, True)

        msg = berm_const.MSG_TEMPLATE.format(
            historic_days_over_low + forecast_days_over_low,
            historic_days_over_low,
            forecast_days_over_low
            )
        mqtt_client.publish(berm_const.MQTT_TOPIC, msg)

        return msg

    except TimeoutError:
        print((berm_const.ERR_TIMEOUT).format(
            berm_const.CONF_MQTT_BROKER_ADDRESS)
            )
        sys.exit(1)


def main():
    """Start Bermuda script."""
    print("Starting bermuda")
    ensure_config_path()
    config = get_config()
    msg = publish_growing_days(config)
    print(msg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
