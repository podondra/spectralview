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

Or if there is already a database created::

    $ docker start <container-name>

To start the application instance write::

    $ spectralview

Finally open your web browser on http://localhost:8000.

Testing
-------

Pytest is test framework that ensures quality of code of this project. Run the
test with::

    $ pytest tests

On GitHub it also collects coverage information. In order to see coverage
locally run::

    $ pytest tests --cov

Releases
--------

Spectral View should follow :pep:`440` -- Version Identification and Dependency
Specification. To make new release the version should be changed in :code:`setup.py` and :code:`docs/conf.py`. Then push new tag to GitHub and the realese will be automatically published on PyPi::

    $ git tag 0.0.0
    $ git push --tags
