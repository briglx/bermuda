**********************************
Bermuda Growing Days
**********************************
The ``bermuda`` script is a support application that will fetch the number of days that are warm enough for bermuda to grow. 

- Development: https://github.com/lamoreauxlab/home-assistant-bermuda/

Bermuda will actively grown when nighttime temperatures are above 60°F.

The ``bermuda`` script calls the DarkSky_ api  to look at 1 week of historic temperature and 1 week of forecast temperatures.

It then publishes a message to a MQTT broker in the format:

.. code-block:: javascript

    {
        "totalDaysAbove60Deg": 11, 
        "historicDaysAbove60Deg":4,
        "forcastDaysAbove60Deg":7
    }


Installing
==========

Create System user::

    useradd  --system  bermuda
    sudo usermod -a -G bermuda bermuda

    su -s /bin/bash bermuda

Create path and environment::

    mkdir /etc/bermuda
    cd /etc/bermuda
    git clone git@github.com:user/project.git .
    python3 -m venv env
    source /etc/bermuda/env/bin/activate
    python3 -m pip install -r requirements.txt

Create config file call config.yaml and add the following settings::

    home_latitude: your_home_latitude
    home_longitude: your_home_longitude
    dark_sky_api_key: your_dark_sky_api_key
    mqtt_broker_address: your_mqtt_broker_address
    mqtt_broker_username: your_mqtt_broker_username
    mqtt_broker_password: your_mqtt_broker_password
    mqtt_broker_port: your_mqtt_broker_port



.. _DarkSky: https://darksky.net/dev/docs

Use
==========

.. code-block:: python

    $ sudo -u bermuda -H -s
    $ source /etc/bermuda/bermuda/bin/activate && python3 /etc/bermuda/bermuda.py