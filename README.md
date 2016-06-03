# Stepmania Server

Implementation of a stepmania server in python3

It's still in progress. But you can actually play with it, and the score will be saved in a database

Things to do:
* Chan functions (color, information about who win the games, ...)
* User privileges (moderator, administrator, of a room/server)
* Web interface (Upload SM file to the server, see results, search for packs, ...)


## Requirement

The StepmaniaServer is written in python3. (>= 3.2)

You need the following dependency :

* pyyaml
* sqlalchemy (>=1.0)
* A database binding. One supports by sqlalchemy.

## Setup

```
sudo python3 setup.py install
```

Launch the stepmania server:

```
smserver
```

## Configuration

To change the configuration, edit the file:
```
/etc/smserver/conf.yml
```

Or pass options to smserver call. Eg :
```
smserver --name MyStepmaniaServer --motd "Welcome on my new server!"
```


