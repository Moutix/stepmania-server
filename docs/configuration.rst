Advanced configuration
======================

Introduction
------------

The configuration file is a YAML file located in /etc/smserver/conf.yml

The location of this file can be modified by using **config** option:

.. code-block:: console

    $ smserver --config "/Configuration/file/location"


You can also force some configuration parameters by passing argument on smserver.

EG.

.. code-block:: console

    $ smserver -name "Server's Name"

This command will force the server.name to be "Server's Name"

Command line only
-----------------

All the command line option can be view by using ``--help``.

.. code-block:: console

    $ smserver --help

Some option can only be passed via command line.


* ``-c`` or ``--config``

Specify the configuration file location.

* ``--update_schema``

Passing this command to smserver will drop all the db tables and recreate them. Use it only if you now what you're doing. You will lost all you're data.


Configuration File
------------------

The configuration file is a YAML file.

Server section
**************

* **name**: Name of the server.
* **motd**: Message display on player's connections
* **ip**: IP the server is supposed to listen (default to 0.0.0.0)
* **port**: Port to use, actually stepmania only support the default port (default to 8765)
* **fps**: Refresh time of the process in background (in second). (default to 1)
* **readtimeout**: Not implemented yet
* **max_users**: NB max of users on the server (default to infinite)
* **type**: Type of server to use. Just choose between async and classic. See next section for details

Additional Servers section
**************************

This section allow you to listen on many interface (UDP + TCP + websocket for instance)

* **ip**: IP the server is supposed to listen
* **port**: Port to use
* **type**: Type of the server

Type available:

* **classic**: (default): Use one thread by client
* **async**: Use a Asyncio server
* **websocket**: Use a websocket server. Expect JSON data
* **udp**: Listen on UDP for messages. Use it for discovery purposes

Database section
****************

* **type**: *mysql*, *pgsql* or *sqlite* (or another support by sqlalchemy)
* **user**: User
* **password**: Password
* **database**: Name of your database, or filename for sqlite
* **host**: Host
* **port**: Port
* **driver**: Driver to use (optional).

See `sqlalchemy manuel <http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls>`_ for more information about database configuration

Example for mysql:

.. code-block:: yaml

   database:
       type: "mysql"
       user: stepmania
       password: ******
       database: stepmania
       host: localhost
       port:
       driver: pymysql

Ban IPs section
***************

A list of the IP you will never allow on the server

Score section
*************

Define here how the XP and percentage are calculated. By default the percentage configuration is the same than the default stepmania theme.

Logger section
**************

Define here the logging configuration.

* **file**: Log to a file
* **stderr**: Log to the standart error output
* **level**: Level of logging (debug, info, warning, error)

Configuration for logging information level in a file and warning in stderr:

.. code-block:: yaml

    stderr:
        level: "warning"
    file:
        level: "info"
        file: "/tmp/stepmania.log"

Rooms section
*************

Define here the static room on your server

* **name**: Name of your room, as shown in the room list
* **password**: Password. Leave empty if it's an open room
* **description**: Password
* **motd**: mesage display on user connection
* **max_users**: nb max of users allow in this room (max to 255)

