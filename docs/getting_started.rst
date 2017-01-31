Getting Started
===============

Installation
------------

Firstly install Spectral View into virtual environment::

    $ pyton3 -m venv venv
    $ source venv/bin/activate
    $ pip install spectralvie

Than start MongoDB possibly in Docker::

    $ docker run --name <container-name> -d mongo
    $ docker inspect <container-name>

Finally run the web application::

    $ spectralview --db_ip=<mongodb-ip> --db_port=<mongodb-port>
