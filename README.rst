Spectral View
=============

.. image:: https://travis-ci.org/podondra/spectralview.svg?branch=master
    :target: https://travis-ci.org/podondra/spectralview
    :alt: Continuous Integration Status

.. image:: https://readthedocs.org/projects/spectralview/badge/?version=latest
    :target: http://spectralview.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/podondra/spectralview/badge.svg?branch=master
    :target: https://coveralls.io/github/podondra/spectralview?branch=master
    :alt: Coverage Status

`Documentation <http://spectralview.readthedocs.io/>`_ is available on
`Read the Docs <https://readthedocs.org/>`_.

Spectral View is web browser tool for classification of Ondřejov CCD700
spectral archive. It is written in Python using
`Tornado Web Framework <http://www.tornadoweb.org/en/stable/>`_
and `Motor <https://motor.readthedocs.io/en/stable/>`_
which is asynchronous driver for MongoDB.
Vizualizations are created with `D3.js <https://d3js.org/>`_.
Source code is available on
`GitHub <https://github.com/podondra/spectralview>`_.

Spectra are divided into five classes:

- unclassified,
- emission,
- absoption,
- double peak and
- unknown.

Import into unclassified class is done through a
`SSAP Service <http://www.ivoa.net/documents/SSA/>`_.
Unclassified spectra are that split into corresponding class by a user
who is presented with vizualization of full spectrum, H-alpha region and
denoised respectively convolved H-alpha region.
Classified spectra can be viewed and move between classes on demand.
