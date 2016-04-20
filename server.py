#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys

from smutils import smserver, smpacket
import conf

class StepmaniaServer(smserver.StepmaniaServer):
    def __init__(self, config):
        self.config = config
        smserver.StepmaniaServer.__init__(self,
                                          config.server["ip"],
                                          config.server["port"])

    def on_nschello(self, serv, packet):
        serv.send(smpacket.SMPacketServerNSCHello(
            version=128,
            name=self.config.server["name"]))

    def on_login(self, serv, packet):
        print(packet)

def main():
    config = conf.Conf(*sys.argv[1:])

    StepmaniaServer(config).start()

if __name__ == "__main__":
    main()

