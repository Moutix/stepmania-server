#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys

from smutils import smserver, smpacket
import conf
from pluginmanager import PluginManager
from authplugin import AuthPlugin

class StepmaniaServer(smserver.StepmaniaServer):
    def __init__(self, config):
        self.config = config
        self.auth = PluginManager.import_plugin(
            'auth.%s' % config.auth["plugin"],
            "AuthPlugin",
            default=AuthPlugin)

        self.plugins = PluginManager("StepmaniaPlugin", config.plugins, "plugins", "plugin")

        smserver.StepmaniaServer.__init__(self,
                                          config.server["ip"],
                                          config.server["port"])

    def on_nschello(self, serv, packet):
        serv.send(smpacket.SMPacketServerNSCHello(
            version=128,
            name=self.config.server["name"]))

    def on_login(self, serv, packet):
        approval, text = self.auth.login(packet["login"], packet["password"])

        serv.send(smpacket.SMPacketServerNSCUOpts(
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

