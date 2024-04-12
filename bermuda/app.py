#!/usr/bin/env python3
"""Bermuda Growing Day script."""

import argparse
from datetime import datetime, timedelta, timezone
import functools
import os
import sys

import forecastio
import paho.mqtt.client as mqtt
import yaml

from bermuda import const as berm_const


def get_arguments(args):
    """Get parsed passed in arguments."""
    parser = argparse.ArgumentParser(description="Bermuda: Forecast, Alert.")
    parser.add_argument("--version", action="version", version=berm_const.__version__)
    parser.add_argument(
        "-c",
        "--config",
        metavar="path_to_config_dir",
        default="",
        help="Directory that contains the Bermuda configuration",
    )

    arguments = parser.parse_args(args)

    return arguments


def ensure_config_path(config_dir, conf_name=berm_const.CONFIG_PATH):
    """Check if config file exists."""
    if not os.path.isdir(config_dir):
        print((berm_const.ERR_CONFIG).format(config_dir))
        sys.exit(1)

    config_file = os.path.join(config_dir, conf_name)
    if not os.path.isfile(config_file):
        print((berm_const.ERR_CONFIG).format(config_file))
        sys.exit(1)

    return config_file


def get_config(config_file):
    """Get configuration."""
    with open(config_file, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    return cfg


@functools.lru_cache(maxsize=14)
def get_historic(dark_sky_api_key, home_latitude, home_longitude, time):
    """Get historic weather with cache."""
    forecast = forecastio.load_forecast(
        dark_sky_api_key, home_latitude, home_longitude, time
    )

    daily = forecast.daily()

    return daily


def get_weather(conf):
    """Get historic and forecast weather data."""
    cur_time = datetime.now(timezone.utc)
    cur_time = cur_time.replace(hour=0, minute=0, second=0, microsecond=0)
    last_week = cur_time - timedelta(days=7)

    historic_data = []

    # Have to call for each day for historic
    for i in range(7):
        prev_day = last_week + timedelta(days=i)
        daily = get_historic(
            conf[berm_const.CONF_DARKSKY_API_KEY],
            conf[berm_const.CONF_HOME_LATITUDE],
            conf[berm_const.CONF_HOME_LONGITUDE],
            time=prev_day,
        )
        historic_data.extend(daily.data)

    # Get Forecast
    forecast = forecastio.load_forecast(
        conf[berm_const.CONF_DARKSKY_API_KEY],
        conf[berm_const.CONF_HOME_LATITUDE],
        conf[berm_const.CONF_HOME_LONGITUDE],
    )
    daily = forecast.daily()

    return (historic_data, daily.data)


def is_in_range(data):
    """Check if data is in range."""
    return (
        data.apparentTemperatureHigh > berm_const.OVERSEED_DAYTIME_LOW
        and data.apparentTemperatureHigh < berm_const.OVERSEED_DAYTIME_HIGH
    ) and (
        data.apparentTemperatureLow > berm_const.OVERSEED_NIGHTIME_LOW
        and data.apparentTemperatureLow < berm_const.OVERSEED_NIGHTIME_HIGH
    )


def get_ideal_overseeding_days(conf):
    """Get number of ideal overseeding days."""
    ideal_growing_days = 0

    historic_data, forcast_data = get_weather(conf)
    combigned_data = historic_data
    combigned_data.extend(forcast_data)

    for data in combigned_data:
        if is_in_range(data):
            ideal_growing_days += 1

    return ideal_growing_days


def get_days(conf, historic=False):
    """Get number of ideal growing days for bermuda."""
    days_over_low = 0

    historic_data, forcast_data = get_weather(conf)

    if historic:
        for data in historic_data:
            if data.apparentTemperatureLow > berm_const.LOW_TEMP:
                days_over_low += 1
    else:
        for data in forcast_data:
            if data.apparentTemperatureLow > berm_const.LOW_TEMP:
                days_over_low += 1

    return days_over_low


def publish_growing_days(conf):
    """Publish the number of growing days to the mqtt broker."""
    try:
        # Connect to Mqqt broker
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        mqtt_client.username_pw_set(
            conf[berm_const.CONF_MQTT_BROCKER_USERNAME],
            conf[berm_const.CONF_MQTT_BROKER_PASSWORD],
        )
        mqtt_client.connect(
            conf[berm_const.CONF_MQTT_BROKER_ADDRESS],
            conf[berm_const.CONF_MQTT_BROKER_PORT],
        )

        # Get Forecast Count
        forecast_days_over_low = get_days(conf)

        # Get historic count
        historic_days_over_low = get_days(conf, True)

        msg = berm_const.MSG_GROWING_TEMPLATE.format(
            historic_days_over_low + forecast_days_over_low,
            historic_days_over_low,
            forecast_days_over_low,
        )
        mqtt_client.publish(berm_const.MQTT_GROWING_TOPIC, msg)

        return msg

    except TimeoutError:
        print((berm_const.ERR_TIMEOUT).format(berm_const.CONF_MQTT_BROKER_ADDRESS))
        sys.exit(1)


def publish_overseeding_days(conf):
    """Publish the number of overseeding days to the mqtt broker."""
    try:
        # Connect to Mqqt broker
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        mqtt_client.username_pw_set(
            conf[berm_const.CONF_MQTT_BROCKER_USERNAME],
            conf[berm_const.CONF_MQTT_BROKER_PASSWORD],
        )
        mqtt_client.connect(
            conf[berm_const.CONF_MQTT_BROKER_ADDRESS],
            conf[berm_const.CONF_MQTT_BROKER_PORT],
        )

        # Get Day Count
        ideal_overseeding_days = get_ideal_overseeding_days(conf)

        msg = berm_const.MSG_OVERSEED_TEMPLATE.format(ideal_overseeding_days)
        mqtt_client.publish(berm_const.MQTT_OVERSEED_TOPIC, msg)

        return msg

    except TimeoutError:
        print((berm_const.ERR_TIMEOUT).format(berm_const.CONF_MQTT_BROKER_ADDRESS))
        sys.exit(1)


def main():
    """Start Bermuda script."""
    print("Starting bermuda")
    args = get_arguments(sys.argv[1:])

    config_dir = args.config
    config_file = ensure_config_path(config_dir)
    config = get_config(config_file)

    msg = publish_growing_days(config)
    print(msg)
    msg = publish_overseeding_days(config)
    print(msg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
