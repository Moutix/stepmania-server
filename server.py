#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys

from smutils import smserver, smpacket
import conf
from pluginmanager import PluginManager
from authplugin import AuthPlugin
from database import DataBase
import logger

class StepmaniaServer(smserver.StepmaniaServer):
    def __init__(self, config):
        self.config = config

        self.log = logger.Logger(config.logger).logger

        self.log.debug("Configuration loaded")

        self.log.debug("Init database")
        self.db = DataBase(
            type=config.database.get("type", 'sqlite'),
            database=config.database.get("database"),
            user=config.database.get("user"),
            password=config.database.get("password"),
            host=config.database.get("host"),
            port=config.database.get("port"),
            driver=config.database.get("driver"),
        )

        self.db.create_tables()

        self.auth = PluginManager.import_plugin(
            'auth.%s' % config.auth["plugin"],
            "AuthPlugin",
            default=AuthPlugin)(self, config.auth["autocreate"])

        self.log.debug("Load Plugins")
        self.plugins = PluginManager("StepmaniaPlugin", config.plugins, "plugins", "plugin")
        self.log.debug("Plugins loaded")

        self.log.debug("Start server")
        smserver.StepmaniaServer.__init__(self,
                                          config.server["ip"],
                                          config.server["port"])

    def on_nschello(self, serv, packet):
        serv.send(smpacket.SMPacketServerNSCHello(
            version=128,
            name=self.config.server["name"]))

    def on_login(self, serv, packet):
        connected = self.auth.login(packet["username"], packet["password"])

        if connected:
            approval = 0
            text = "Successfully Login"
            self.log.info("Player %s successfully login" % packet["username"])
        else:
            approval = 1
            text = "Connection failed"
            self.log.info("Player %s failed to connect" % packet["username"])

        serv.send(smpacket.SMPacketServerNSSMONL(
            packet=smpacket.SMOPacketServerLogin(
                approval=approval,
                text=text
            )
        ))

def main():
    config = conf.Conf(*sys.argv[1:])

    StepmaniaServer(config).start()

if __name__ == "__main__":
    main()

