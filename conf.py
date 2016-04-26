#!/usr/bin/env python3
# -*- coding: utf8 -*-

from io import open
import argparse
import sys
import yaml

class Conf(dict):
    parser = argparse.ArgumentParser(description='Stepmania configuration')
    parser.add_argument('-name', '--server.name',
                        dest='server.name',
                        help="Server's name",
                        default="Stepmania")

    parser.add_argument('-motd', '--server.motd',
                        dest='server.motd',
                        help="Server's description",
                        default="Welcome to this stepmania server")

    parser.add_argument('-ip', '--server.ip',
                        dest='server.ip',
                        help="IP to listen to (default: 0.0.0.0)",
                        default="0.0.0.0")

    parser.add_argument('-port', '--server.port',
                        dest='server.port',
                        type=int,
                        help="Port to listen to (default: 8765)",
                        default=8765)

    parser.add_argument('--auth.plugin',
                        dest='auth.plugin',
                        type=str,
                        help="Plugin to use for auth (default: database)",
                        default='database')

    parser.add_argument('--auth.autocreate',
                        dest='auth.autocreate',
                        type=bool,
                        help="Create user on first connection",
                        default=True)

    parser.add_argument('-c', '--config',
                        dest='config',
                        help="Server's configuration file (default: conf.yml)",
                        default="conf.yml")

    def __init__(self, *args):
        dict.__init__(self)
        self._args = self.parser.parse_args(args)

        with open(self._args.config, 'r', encoding='utf-8') as stream:
            self.update(yaml.load(stream), allow_unicode=True)

        for key, value in vars(self._args).items():
            self._add_to_conf(key, value)

        self.server = self["server"]
        self.auth = self["auth"]
        self.plugins = self.get("plugins", [])

    def _add_to_conf(self, arg, value, conf=None):
        if not conf:
            conf = self

        arg = arg.split(".")
        arg.reverse()
        while True:
            option = arg.pop()
            if not arg:
                conf[option] = value
                return

            if option not in conf:
                conf[option] = {}

            conf = conf[option]

if __name__ == "__main__":
    print(Conf(*sys.argv[1:]))
