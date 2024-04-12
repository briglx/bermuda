"""The tests for the bermuda script."""

import os
from unittest.mock import patch

import paho.mqtt.client as mqtt
import pytest

from bermuda import const as berm_const
from bermuda.app import (
    ensure_config_path,
    get_arguments,
    get_config,
    get_ideal_overseeding_days,
    main,
    publish_growing_days,
    publish_overseeding_days,
)


def get_test_config():
    """Return a test config settings."""
    return {
        berm_const.CONF_HOME_LATITUDE: 22,
        berm_const.CONF_HOME_LONGITUDE: -11,
        berm_const.CONF_DARKSKY_API_KEY: "mytestkey",
        berm_const.CONF_MQTT_BROKER_ADDRESS: "192.0.2.0",
        berm_const.CONF_MQTT_BROCKER_USERNAME: "homeassistant",
        berm_const.CONF_MQTT_BROKER_PASSWORD: "mypassword",
        berm_const.CONF_MQTT_BROKER_PORT: 19750,
    }


def test_publish_growing_days():
    """Test the publish growing days."""
    patch_forecast = "bermuda.app.forecastio"
    patch_mqtt_client = "bermuda.app.mqtt.Client"
    with patch(patch_forecast), patch(patch_mqtt_client) as mock_mqtt_client:

        # Get call
        conf = get_test_config()
        msg = publish_growing_days(conf)

        # Test mocks
        mock_mqtt_client.assert_called_once_with(mqtt.CallbackAPIVersion.VERSION2)
        mock_instance = mock_mqtt_client.return_value
        mock_instance.username_pw_set.assert_called_once_with(
            conf[berm_const.CONF_MQTT_BROCKER_USERNAME],
            conf[berm_const.CONF_MQTT_BROKER_PASSWORD],
        )
        mock_instance.connect.assert_called_once_with(
            conf[berm_const.CONF_MQTT_BROKER_ADDRESS],
            conf[berm_const.CONF_MQTT_BROKER_PORT],
        )
        mock_instance.publish.assert_called_once_with(
            berm_const.MQTT_GROWING_TOPIC, msg
        )

        # Test Message
        test_msg = berm_const.MSG_GROWING_TEMPLATE.format(0, 0, 0)
        assert msg == test_msg


def mock_load_forecast():
    """Mock Load Forecast."""
    return {"daily"}


# pylint: disable=R0903
class MockGrowingForecastData:
    """Mock Forecast Data object."""

    def __init__(self):
        """Init for mock."""
        # pylint: disable=C0103
        self.apparentTemperatureHigh = 95
        self.apparentTemperatureLow = 80


# pylint: disable=R0903
class MockOverseedingForecastData:
    """Mock Forecast Data object."""

    def __init__(self):
        """Init for mock."""
        # pylint: disable=C0103
        self.apparentTemperatureHigh = 80
        self.apparentTemperatureLow = 55


# pylint: disable=R0903
class MockGrowingForecastDaily:
    """MOck Forecast Daily object."""

    def __init__(self):
        """Init for mock."""
        self.data = [MockGrowingForecastData()]


# pylint: disable=R0903
class MockOverseedingForecastDaily:
    """MOck Forecast Daily object."""

    def __init__(self):
        """Init for mock."""
        self.data = [MockOverseedingForecastData()]


# pylint: disable=R0903
class MockGrowingForecast:
    """Mock Forecast object."""

    @classmethod
    def daily(cls):
        """Return mock daily forecast."""
        return MockGrowingForecastDaily()


# pylint: disable=R0903
class MockOverseedingForecast:
    """Mock Forecast object."""

    @classmethod
    def daily(cls):
        """Return mock daily forecast."""
        return MockOverseedingForecastDaily()


# pylint: disable=R0903
class MockArgs:
    """Mock args object."""

    def __init__(self):
        """Init for mock."""
        self.config = "test_config"


def test_publish_growing_days_data():
    """Test the publish growing days with data."""
    patch_forecast = "bermuda.app.forecastio"
    patch_mqtt_client = "bermuda.app.mqtt.Client"
    patch_get_historic = "bermuda.app.get_historic"
    with (
        patch(patch_forecast) as mock_forecastio,
        patch(patch_mqtt_client) as mock_mqtt_client,
        patch(patch_get_historic, autospec=True) as mock_get_historic,
    ):
        # Override the forecastio.load_forecast method
        mock_forcast = MockGrowingForecast()
        mock_forecastio.load_forecast.return_value = mock_forcast
        mock_daily = MockGrowingForecastDaily()
        mock_get_historic.return_value = mock_daily

        # Get call
        conf = get_test_config()
        msg = publish_growing_days(conf)

        # Test mqtt Client
        mock_mqtt_client.assert_called_once_with(mqtt.CallbackAPIVersion.VERSION2)
        mock_instance = mock_mqtt_client.return_value
        mock_instance.username_pw_set.assert_called_once_with(
            conf[berm_const.CONF_MQTT_BROCKER_USERNAME],
            conf[berm_const.CONF_MQTT_BROKER_PASSWORD],
        )
        mock_instance.connect.assert_called_once_with(
            conf[berm_const.CONF_MQTT_BROKER_ADDRESS],
            conf[berm_const.CONF_MQTT_BROKER_PORT],
        )
        mock_instance.publish.assert_called_once_with(
            berm_const.MQTT_GROWING_TOPIC, msg
        )

        # Test Message
        test_msg = berm_const.MSG_GROWING_TEMPLATE.format(8, 7, 1)
        assert msg == test_msg


def test_ideal_overseeding_days():
    """Test the ideal growing days."""
    patch_forecast = "bermuda.app.forecastio"
    patch_get_historic = "bermuda.app.get_historic"
    with (
        patch(patch_forecast) as mock_forecastio,
        patch(patch_get_historic, autospec=True) as mock_get_historic,
    ):
        # Override the forecastio.load_forecast method
        mock_forcast = MockOverseedingForecast()
        mock_forecastio.load_forecast.return_value = mock_forcast
        mock_daily = MockOverseedingForecastDaily()
        mock_get_historic.return_value = mock_daily

        # Get call
        config = get_test_config()
        days = get_ideal_overseeding_days(config)

        assert days == 8

        assert mock_get_historic.call_count == 7

        mock_forecastio.load_forecast.assert_called_with(
            config[berm_const.CONF_DARKSKY_API_KEY],
            config[berm_const.CONF_HOME_LATITUDE],
            config[berm_const.CONF_HOME_LONGITUDE],
        )


def test_publish_overseeding_days_data():
    """Test the publish overseeding days with data."""
    patch_forecast = "bermuda.app.forecastio"
    patch_mqtt_client = "bermuda.app.mqtt.Client"
    patch_get_historic = "bermuda.app.get_historic"
    with (
        patch(patch_forecast) as mock_forecastio,
        patch(patch_mqtt_client) as mock_mqtt_client,
        patch(patch_get_historic, autospec=True) as mock_get_historic,
    ):
        # Override the forecastio.load_forecast method
        mock_forcast = MockOverseedingForecast()
        mock_forecastio.load_forecast.return_value = mock_forcast
        mock_daily = MockOverseedingForecastDaily()
        mock_get_historic.return_value = mock_daily

        # Get call
        conf = get_test_config()
        msg = publish_overseeding_days(conf)

        # Test mqtt Client
        mock_mqtt_client.assert_called_once_with(mqtt.CallbackAPIVersion.VERSION2)
        mock_instance = mock_mqtt_client.return_value
        mock_instance.username_pw_set.assert_called_once_with(
            conf[berm_const.CONF_MQTT_BROCKER_USERNAME],
            conf[berm_const.CONF_MQTT_BROKER_PASSWORD],
        )
        mock_instance.connect.assert_called_once_with(
            conf[berm_const.CONF_MQTT_BROKER_ADDRESS],
            conf[berm_const.CONF_MQTT_BROKER_PORT],
        )
        mock_instance.publish.assert_called_once_with(
            berm_const.MQTT_OVERSEED_TOPIC, msg
        )

        # Test Message
        test_msg = berm_const.MSG_OVERSEED_TEMPLATE.format(8)
        assert msg == test_msg


def test_growing_days_mqtt_connection_timeout():
    """Test Response to mqtt timeout."""
    with pytest.raises(SystemExit) as ex:
        config = get_test_config()
        publish_growing_days(config)

        assert ex.value_code == 1


def test_overseed_mqtt_connection_timeout():
    """Test Response to mqtt timeout."""
    with pytest.raises(SystemExit) as ex:
        config = get_test_config()
        publish_overseeding_days(config)

        assert ex.value_code == 1


def test_arguments():
    """Test arguments passed to bermuda."""
    args = get_arguments(["--config", "path/to/config"])
    config_dir = args.config
    assert config_dir == "path/to/config"


def get_test_config_dir(*add_path):
    """Return a path to a test config dir."""
    return os.path.join(os.path.dirname(__file__), os.pardir, *add_path)


def test_config_path():
    """Test config path."""
    config_dir = get_test_config_dir()
    config_file = ensure_config_path(config_dir, "config-example.yaml")

    assert config_file == os.path.join(config_dir, "config-example.yaml")


def test_config_bad_path():
    """Test config path."""
    config_dir = "bad/path"

    with pytest.raises(SystemExit) as ex:
        ensure_config_path(config_dir, "config-example.yaml")

        assert ex.value_code == 1


def test_config_bad_file():
    """Test config path."""
    config_dir = get_test_config_dir()

    with pytest.raises(SystemExit) as ex:
        ensure_config_path(config_dir, "bad_config-example.yaml")

        assert ex.value_code == 1


def test_get_config():
    """Test get config yaml."""
    config_dir = get_test_config_dir()
    config_file = os.path.join(config_dir, "config-example.yaml")
    config = get_config(config_file)

    assert config[berm_const.CONF_MQTT_BROKER_ADDRESS] == "192.0.2.0"


def test_main():
    """Test Main method."""
    path_args = "bermuda.app.get_arguments"
    patch_path = "bermuda.app.ensure_config_path"
    patch_config = "bermuda.app.get_config"
    patch_days = "bermuda.app.publish_growing_days"
    patch_overseed_days = "bermuda.app.publish_overseeding_days"

    with (
        patch(path_args) as mock_args,
        patch(patch_path) as mock_path,
        patch(patch_config) as mock_config,
        patch(patch_days) as mock_days,
        patch(patch_overseed_days) as mock_overseed,
    ):

        mock_args.return_value = MockArgs()
        mock_path.return_value = "testpath"
        mock_config.return_value = "test_config"
        mock_days.return_value = "testing"
        mock_overseed.return_value = "testing"

        resp = main()

        assert mock_args.call_count == 1
        mock_path.assert_called_once_with("test_config")
        mock_config.assert_called_once_with("testpath")
        mock_days.assert_called_once_with("test_config")
        mock_overseed.assert_called_once_with("test_config")

        assert resp == 0
