.. SMServer documentation master file, created by
   sphinx-quickstart on Wed Jun 29 21:15:43 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SMServer's documentation!
====================================

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

For Windows:

* :download:`win-smserver.zip`

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
        user: stepmania
        password: *******
        database: stepmania
        host: localhost
        port:
        driver: pymysql

To launch the server just type:

.. code-block:: console

    $ smserver

For advanced option/configuration, type ``--help`` or see :doc:`configuration`

Source code
-----------

You can find the last version of the server on `github <https://github.com/ningirsu/stepmania-server>`_


License
-------

This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.

Contents
--------

.. toctree::
   :maxdepth: 2

   configuration
   protocol
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

