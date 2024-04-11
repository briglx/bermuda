"""The tests for the bermuda script."""
from unittest.mock import patch
from datetime import datetime, timedelta
from bermuda.app import publish_growing_days
import bermuda.const as berm_const


def get_test_config():
    return {
        berm_const.CONF_HOME_LATITUDE: 22,
        berm_const.CONF_HOME_LONGITUDE: -11,
        berm_const.CONF_DARKSKY_API_KEY: 'mytestkey',
        berm_const.CONF_MQTT_BROKER_ADDRESS: '192.0.2.0',
        berm_const.CONF_MQTT_BROCKER_USERNAME: 'homeassistant',
        berm_const.CONF_MQTT_BROKER_PASSWORD: 'mypassword',
        berm_const.CONF_MQTT_BROKER_PORT: 19750
        }


def test_publish_growing_days():
    PATCH_FORECAST = 'bermuda.app.forecastio'
    PATCH_MQTT = 'bermuda.app.mqtt'
    with patch(PATCH_FORECAST) \
            as mock_forecastio, patch(PATCH_MQTT) \
            as mock_mqtt:

        # Get call
        config = get_test_config()
        msg = publish_growing_days(config)

        # Test mocks
        mock_mqtt.Client.assert_called_with()

        cur_time = datetime.utcnow()
        cur_time = cur_time.replace(minute=0, second=0, microsecond=0)
        last_week = cur_time - timedelta(days=7)

        mock_forecastio.load_forecast.assert_called_with(
            config[berm_const.CONF_DARKSKY_API_KEY],
            config[berm_const.CONF_HOME_LATITUDE],
            config[berm_const.CONF_HOME_LONGITUDE],
            time=last_week
        )

        # Test Message
        test_msg = berm_const.MSG_TEMPLATE.format(0, 0, 0)
        assert(msg == test_msg)
