**********************************
Bermuda Growing Days
**********************************
.. image:: https://coveralls.io/repos/github/briglx/bermuda/badge.svg?branch=master
    :target: https://coveralls.io/github/briglx/bermuda?branch=master
    :alt: Code Coverage Status

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

Setup
=====

Installing
----------

Get Code::

    $ git clone https://github.com/briglx/bermuda.git
    $ cd bermuda/
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ python3 -m pip install .

Edit Configuration::

    $ cp config-example.yaml config.yaml
    $ cp example.env .env

Config Settings:

- home_latitude: Latitude coordinate to monitor weather.
- home_longitude: Longitude coordinate to monitor weather
- dark_sky_api_key: Your API key for Dark Sky.
- mqtt_brocker_address: The IP address or hostname of your MQTT broker example 192.0.2.0.
- mqtt_broker_username: The username to use with your MQTT broker.
- mqtt_broker_password: The corresponding password for the username to use with your MQTT broker.
- mqtt_broker_port: The network port to connect to.

Run Bermuda manually::

    $ berm --config /path/to/config/dir/

Create Cron Job
---------------

Create a bash script called bermuda.sh to run bermuda::

    #!/bin/bash
    /path/to/bermuda/env/bin/python3 /path/to/bermuda/app.py --config /path/to/bermuda/config

Edit the file be executable::

    $ chmod +x bermuda.sh

Configure Cron Job to run everyday at 2am::

    $ sudo crontab -e

    0 2 * * * /path/to/bermuda.sh

Optional Create a system user
-----------------------------

Create System user and group::

    useradd  --system  bermuda
    sudo usermod -a -G bermuda bermuda

Development
===========

You'll need to set up a development environment if you want to develop a new feature or fix issues. The project uses a docker based devcontainer to ensure a consistent development environment.
- Open the project in VSCode and it will prompt you to open the project in a devcontainer. This will have all the required tools installed and configured.

Setup local dev environment
---------------------------

If you want to develop outside of a docker devcontainer you can use the following commands to setup your environment.

* Install Python
* Install Azure CLI
* Configure linting and formatting tools

.. code-block:: bash

    # Configure the environment variables. Copy example.env to .env and update the values
    cp example.env .env

    # load .env vars
    # [ ! -f .env ] || export $(grep -v '^#' .env | xargs)
    # or this version allows variable substitution and quoted long values
    # [ -f .env ] && while IFS= read -r line; do [[ $line =~ ^[^#]*= ]] && eval "export $line"; done < .env

    # Create and activate a python virtual environment
    # Windows
    # virtualenv \path\to\.venv -p path\to\specific_version_python.exe
    # C:\Users\!Admin\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
    # .venv\scripts\activate

    # Linux
    # virtualenv .venv /usr/local/bin/python3.12
    # python3.12 -m venv .venv
    # python3 -m venv .venv
    python3 -m venv .venv
    source .venv/bin/activate

    # Update pip
    python -m pip install --upgrade pip

    # Install dependencies
    pip install -r requirements_dev.txt

    # Configure linting and formatting tools
    sudo apt-get update
    sudo apt-get install -y shellcheck
    pre-commit install

    # Install the package locally
    pip install --editable .


Style Guidelines
----------------

This project enforces quite strict `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ and `PEP257 (Docstring Conventions) <https://www.python.org/dev/peps/pep-0257/>`_ compliance on all code submitted.

We use `Black <https://github.com/psf/black>`_ for uncompromised code formatting.

Summary of the most relevant points:

- Comments should be full sentences and end with a period.
- `Imports <https://www.python.org/dev/peps/pep-0008/#imports>`_  should be ordered.
- Constants and the content of lists and dictionaries should be in alphabetical order.
- It is advisable to adjust IDE or editor settings to match those requirements.

Use new style string formatting
-------------------------------

Prefer `f-strings <https://docs.python.org/3/reference/lexical_analysis.html#f-strings>`_ over ``%`` or ``str.format``.

.. code-block:: python

    # New
    f"{some_value} {some_other_value}"
    # Old, wrong
    "{} {}".format("New", "style")
    "%s %s" % ("Old", "style")

One exception is for logging which uses the percentage formatting. This is to avoid formatting the log message when it is suppressed.

.. code-block:: python

    _LOGGER.info("Can't connect to the webservice %s at %s", string1, string2)

Testing
--------
Ideally, all code is checked to verify the following:

All the unit tests pass All code passes the checks from the linting tools To run the linters, run the following commands:

.. code-block:: bash

    # Use pre-commit scripts to run all linting
    pre-commit run --all-files

    # Run a specific linter via pre-commit
    pre-commit run --all-files codespell

    # Run linters outside of pre-commit
    codespell .
    shellcheck -x ./script/*.sh
    rstcheck README.rst

    # Run unit tests
    python -m pytest tests
    python -m pytest --cov-report term-missing --cov=bermuda tests/
