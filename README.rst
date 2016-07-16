Stepmania Server
================

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor|
    * - package
      - |version| |supported-versions| |license|

.. |docs| image:: https://readthedocs.org/projects/stepmania-server/badge/?version=latest
    :alt: Documentation Status
    :target: https://stepmania-server.readthedocs.io/

.. |travis| image:: https://travis-ci.org/ningirsu/stepmania-server.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ningirsu/stepmania-server

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/ningirsu/stepmania-server?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ningirsu/stepmania-server

.. |version| image:: https://img.shields.io/pypi/v/smserver.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/smserver

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/smserver.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/smserver

.. |license| image:: https://img.shields.io/pypi/l/smserver.svg?style=flat
    :alt: License
    :target: https://pypi.python.org/pypi/smserver

.. end-badges

SMServer is an implementation of a stepmania server in python3.

The goal is to provide a simple server implementation which can easily be adapt to your need.

Requirement
-----------

SMServer only support python3.3 and higher. It use:

* PYYaml
* SQLAlchemy
* asyncio


Installation
------------

Install the server using pip, or directly from source:

.. code-block:: console

    $ python3 setup.py install

or

.. code-block:: console

    $ pip install smserver


Configuration
-------------

The server will come with a default configuration file located in:

.. code-block:: console

    $ /etc/smserver/conf.yml


By default, the server will use a sqlite database. To change it adapt the database section of the configuration file.

EG for mysql:

.. code-block:: yaml

    database:
        type: "mysql"
        user: "stepmania"
        password: "*******"
        database: "stepmania"
        host: "localhost"
        port:
        driver: "pymysql"

To launch the server just type:

.. code-block:: console

    $ smserver

For more information check the `docs <https://stepmania-server.readthedocs.io/>`_

License
-------

This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.

