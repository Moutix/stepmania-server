#!/usr/bin/env python3
# -*- coding: utf8 -*-

import inspect
import os
try:
    from importlib import reload
except ImportError:
    pass

class StepmaniaPlugin(object):
    def __init__(self, server):
        self.server = server

    def on_packet(self, session, serv, packet):
        pass

    def on_nscping(self, session, serv, packet):
        pass

    def on_nscpingr(self, session, serv, packet):
        pass

    def on_nschello(self, session, serv, packet):
        pass

    def on_nscgsr(self, session, serv, packet):
        pass

    def on_nscgon(self, session, serv, packet):
        pass

    def on_nscgsu(self, session, serv, packet):
        pass

    def on_nscsu(self, session, serv, packet):
        pass

    def on_nsccm(self, session, serv, packet):
        pass

    def on_nscrsg(self, session, serv, packet):
        pass

    def on_nsccuul(self, session, serv, packet):
        pass

    def on_nsscsms(self, session, serv, packet):
        pass

    def on_nscuopts(self, session, serv, packet):
        pass

    def on_nssmonl(self, session, serv, packet):
        func = getattr(self, "on_%s" % packet["packet"].command.name.lower(), None)
        if not func:
            return None

        return func(session, serv, packet["packet"])

    def on_nscformatted(self, session, serv, packet):
        pass

    def on_nscattack(self, session, serv, packet):
        pass

    def on_xmlpacket(self, session, serv, packet):
        pass

    def on_login(self, session, serv, packet):
        pass

    def on_enterroom(self, session, serv, packet):
        pass

    def on_createroom(self, session, serv, packet):
        pass

    def on_roominfo(self, session, serv, packet):
        pass


class PluginError(Exception):
    pass

class PluginManager(dict):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    def __init__(self, plugin_class, paths=None, directory=None, plugin_file=None):
        self.plugin_class = plugin_class
        self.plugin_file = plugin_file
        self.directory = directory
        if paths is None:
            paths = self.all_paths(directory, plugin_file)
        if not paths:
            paths = []

        self.paths = paths

        self.load()

    def all_paths(self, directory, plugin_file):
        paths = []

        directory_path = os.path.join(self.__location__, "/".join(directory.split(".")[1:]))

        for path in os.listdir(directory_path):
            if not os.path.isdir(os.path.join(directory_path, path)):
                continue

            if not os.path.isfile("%s.py" % os.path.join(directory_path, path, plugin_file)):
                continue

            paths.append(path)

        return paths

    def load(self, force_reload=False):
        for path in self.paths:
            fullpath = '.'.join([p for p in (self.directory, path, self.plugin_file) if p is not None])
            self[path] = self.import_plugin(fullpath,
                                            plugin_class=self.plugin_class,
                                            force_reload=force_reload)

    def init(self, *opt):
        for key, app in self.items():
            self[key] = app(*opt)

    @staticmethod
    def import_plugin(path, plugin_class, force_reload=False, default=None):
        module = __import__(path, fromlist=[plugin_class])
        if force_reload:
            reload(module)

        for cls in inspect.getmembers(module, inspect.isclass):
            app = getattr(module, cls[0])
            if app and (plugin_class in [x.__name__ for x in app.__bases__]):
                return app

        return default


if __name__ == "__main__":
    print(PluginManager.import_plugin("auth.database", "AuthPlugin"))
    plugins = PluginManager("StepmaniaPlugin", ["chat"], "plugins", "plugin")
    plugins.load()
    plugins.init("a")
    print(plugins)

    print(PluginManager("StepmaniaController", [], "controllers", "controller"))
