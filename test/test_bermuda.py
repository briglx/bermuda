"""The tests for the bermuda script."""
import os
from unittest.mock import patch
from datetime import datetime, timedelta
import pytest
from bermuda.app import (
    publish_growing_days,
    get_arguments,
    ensure_config_path,
    get_config,
    main
    )
from bermuda import const as berm_const


def get_test_config():
    """Return a test config settings."""
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
    """Test the publish growing days."""
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


def mock_load_forecast():
    """Mock Load Forecast."""
    return {'daily'}


class MockForecastData():
    """Mock Forecast Data object."""

    def __init__(self):
        """Init for mock."""
        self.apparentTemperatureLow = 80


class MockForecastDaily():
    """MOck Forecast Daily object."""

    def __init__(self):
        """Init for mock."""
        self.data = [MockForecastData()]


class MockForecast():
    """Mock Forecast object."""

    def daily(self):
        """Return mock daily forecast."""
        return MockForecastDaily()


class MockArgs():
    """Mock args object."""

    def __init__(self):
        """Init for mock."""
        self.config = "test_config"


def test_publish_growing_days_data():
    """Test the publish growing days with data."""
    PATCH_FORECAST = 'bermuda.app.forecastio'
    PATCH_MQTT = 'bermuda.app.mqtt'
    with patch(PATCH_FORECAST) \
            as mock_forecastio, patch(PATCH_MQTT) \
            as mock_mqtt:

        # Override the forecastio.load_forecast method
        mf = MockForecast()
        mock_forecastio.load_forecast.return_value = mf

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
        test_msg = berm_const.MSG_TEMPLATE.format(2, 1, 1)
        assert(msg == test_msg)


def test_mqtt_connection_timeout():
    """Test Response to mqtt timeout."""
    with pytest.raises(SystemExit) as ex:
        config = get_test_config()
        publish_growing_days(config)

        assert(ex.value_code == 1)


def test_arguments():
    """Test arguments passed to bermuda."""
    args = get_arguments(['--config', 'path/to/config'])
    config_dir = args.config
    assert config_dir == 'path/to/config'


def get_test_config_dir(*add_path):
    """Return a path to a test config dir."""
    return os.path.join(os.path.dirname(__file__), os.pardir, *add_path)


def test_config_path():
    """Test config path."""
    config_dir = get_test_config_dir()
    config_file = ensure_config_path(config_dir, 'config-example.yaml')

    assert config_file == os.path.join(config_dir, 'config-example.yaml')


def test_config_bad_path():
    """Test config path."""
    config_dir = 'bad/path'

    with pytest.raises(SystemExit) as ex:
        ensure_config_path(config_dir, 'config-example.yaml')

        assert ex.value_code == 1


def test_config_bad_file():
    """Test config path."""
    config_dir = get_test_config_dir()

    with pytest.raises(SystemExit) as ex:
        ensure_config_path(config_dir, 'bad_config-example.yaml')

        assert ex.value_code == 1


def test_get_config():
    """Test get config yaml."""
    config_dir = get_test_config_dir()
    config_file = os.path.join(config_dir, 'config-example.yaml')
    config = get_config(config_file)

    assert config[berm_const.CONF_MQTT_BROKER_ADDRESS] == '192.0.2.0'


def test_main():
    """Test Main method."""
    PATH_ARGS = 'bermuda.app.get_arguments'
    PATCH_PATH = 'bermuda.app.ensure_config_path'
    PATCH_CONFIG = 'bermuda.app.get_config'
    PATCH_DAYS = 'bermuda.app.publish_growing_days'

    with patch(PATH_ARGS) as mock_args, \
        patch(PATCH_PATH) as mock_path, \
        patch(PATCH_CONFIG) as mock_config, \
            patch(PATCH_DAYS) as mock_days:

        mock_args.return_value = MockArgs()
        mock_path.return_value = 'testpath'
        mock_config.return_value = 'test_config'
        mock_days.return_value = 'testing'

        resp = main()

        assert mock_args.call_count == 1
        mock_path.assert_called_once_with('test_config')
        mock_config.assert_called_once_with('testpath')
        mock_days.assert_called_once_with('test_config')

        assert resp == 0
