For Developers
===============

Installation
------------

Firstly obtain the source code::

    $ git clone https://github.com/podondra/spectralview.git
    $ cd spectralview

You may create virtualenv in order to avoid dependency problems.
Use Python 3.5+ because this project make heavy use of coroutines::

    $ python3 -m venv venv
    $ source venv/bin/activate

Install the package in editable mode with development dependencies::

    $ pip install -e .[dev]

This application uses MongoDB with Motor driver. One way to install this database is using Docker::

    $ docker run --name <container-name> -d mongo

To start the application instance write::

    $ spectralview

Finally open your web browser on http://localhost:8888.

Tips
----

To resume old MongoDB Docker container issue::

    $ docker start <container-name>
