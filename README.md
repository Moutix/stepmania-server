# Stepmania Server

Stepmania server in python3. Feel free to try it and ask for features!

[![Travis build Status](https://travis-ci.org/ningirsu/stepmania-server.svg?branch=master)](https://travis-ci.org/ningirsu/stepmania-server) [![AppVeyor build status](https://ci.appveyor.com/api/projects/status/129lem90wp1eilu6?svg=true)](https://ci.appveyor.com/project/ningirsu/stepmania-server) [![ReadTheDocs](https://readthedocs.org/projects/pip/badge/?version=latest)](https://stepmania-server.readthedocs.io/)

## Requirement

The StepmaniaServer is written in python3. (>= 3.3)

You need the following dependency :

* pyyaml
* sqlalchemy (>=1.0)
* websockets. Only use if you want the server to listen for websockets package. (Currently useless)
* asyncio (if using python 3.3)
* A database binding. One supports by sqlalchemy.

## Setup

```
sudo python3 setup.py install
```

Launch the stepmania server:

```
smserver
```

If you want to launch the server as a service, check the init.d/systemd script

## Configuration

To change the configuration, edit the file:
```
/etc/smserver/conf.yml
```

Or pass options to smserver call. Eg :
```
smserver --name MyStepmaniaServer --motd "Welcome on my new server!"
```

