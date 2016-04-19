#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys

import conf
from server import StepmaniaServer

def main():
    config = conf.Conf(*sys.argv[1:])

    print(config.server)

    StepmaniaServer(config.server['ip'], config.server['port']).start()

if __name__ == "__main__":
    main()

