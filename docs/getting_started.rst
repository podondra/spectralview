Getting Started
===============

Requirements
------------

This application uses asyncio features so Python3.5 is required.
If you have Python installed you also have :code:`pip` to install other
Python's packages. Lastly you would need Docker to run a MongoDB instance.
See their website form `installation instruction
<https://docs.docker.com/engine/installation/>`_.

Installation
------------

Firstly install Spectral View into virtual environment::

    $ pyton3 -m venv venv
    $ source venv/bin/activate
    $ pip install -U pip setuptools
    $ pip install spectralvie

Than start MongoDB possibly in Docker::

    $ docker run --name <container-name> -d mongo
    $ docker inspect <container-name>

Finally run the web application::

    $ spectralview --db_ip=<mongodb-ip> --db_port=<mongodb-port>
