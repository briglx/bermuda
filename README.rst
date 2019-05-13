**********************************
Bermuda Growing Days
**********************************
.. image:: https://travis-ci.org/briglx/bermuda.svg?branch=master
    :target: https://travis-ci.org/briglx/bermuda
.. image:: https://coveralls.io/repos/github/briglx/bermuda/badge.svg?branch=master
    :target: https://coveralls.io/github/briglx/bermuda?branch=master


The ``bermuda`` script is a support application that will fetch the number of days that are warm enough for bermuda to grow. 

- Development: https://github.com/briglx/bermuda

Bermuda will actively grown when nighttime temperatures are above 60°F.

The ``bermuda`` script calls the DarkSky_ api  to look at 1 week of historic temperature and 1 week of forecast temperatures.

It then publishes a message to a MQTT broker in the format:

.. code-block:: javascript

    {
        "totalDaysAbove60Deg": 11, 
        "historicDaysAbove60Deg":4,
        "forcastDaysAbove60Deg":7
    }

.. _DarkSky: https://darksky.net/dev/docs

Installing
==========

Get Code::

    $ git clone https://github.com/briglx/bermuda.git
    $ cd bermuda/
    $ python3 -m venv env
    $ source env/bin/activate
    $ python3 -m pip install .

Edit Configuration::

    $ cp config-example.yaml config.yaml

Config Settings:

- home_latitude: Latitude coordinate to monitor weather.
- home_longitude: Longitude coordinate to monitor weather
- dark_sky_api_key: Your API key for Dark Sky.
- mqtt_brocker_address: The IP address or hostname of your MQTT broker example 192.0.2.0.
- mqtt_broker_username: The username to use with your MQTT broker.
- mqtt_broker_password: The corresponding password for the username to use with your MQTT broker.
- mqtt_broker_port: The network port to connect to.

Run Bermuda manually::

    $ berm 

Create a system user
====================

Create System user and group::

    useradd  --system  bermuda
    sudo usermod -a -G bermuda bermuda


Autostart with Systemd
======================

Create a file is /etc/systemd/system/bermuda@YOUR_USER.service with YOUR_USER replaced by the user account that Bermuda will run as (normally bermuda).
The following template should work::

    [Unit]
    Description=Bermuda
    After=network-online.target

    [Service]
    Type=simple
    User=%i
    ExecStart=/srv/bermuda/bin/berm

    [Install]
    WantedBy=multi-user.target

Use
==========

.. code-block:: bash

    $ sudo -u bermuda -H -s
    $ source /etc/bermuda/bermuda/bin/activate && python3 /etc/bermuda/bermuda.py