#!/usr/bin/env python3
# -*- coding: utf8 -*-

import inspect
import os
import pkgutil

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

class PluginManager(list):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    def __init__(self, plugin_class, paths=None, directory=None, plugin_file=None):
        if not isinstance(plugin_class, list):
            plugin_class = [plugin_class]

        self.plugin_class = plugin_class

        self.plugin_file = plugin_file
        self.directory = directory
        if paths is None:
            paths = self.all_paths(directory)
        if not paths:
            paths = []

        self.paths = paths

        self.load()

    def all_paths(self, directory):
        directory_path = os.path.join(self.__location__, "/".join(directory.split(".")[1:]))
        for _, name, _ in pkgutil.iter_modules([directory_path]):
            yield name

    def load(self, force_reload=False):
        del self[:]
        for path in self.paths:
            fullpath = '.'.join([p for p in (self.directory, path, self.plugin_file) if p is not None])
            self.extend(self.import_plugin(fullpath,
                                           plugin_classes=self.plugin_class,
                                           force_reload=force_reload))

    def init(self, *opt):
        for idx, app in enumerate(self):
            self[idx] = app(*opt)

    @staticmethod
    def import_plugin(path, plugin_classes, force_reload=False):
        if not isinstance(plugin_classes, list):
            plugin_classes = [plugin_classes]

        module = __import__(path, fromlist=plugin_classes)
        if force_reload:
            reload(module)

        apps = []
        for cls in inspect.getmembers(module, inspect.isclass):
            app = getattr(module, cls[0])
            if not app:
                continue

            for plugin_class in plugin_classes:
                if plugin_class in [x.__name__ for x in app.__bases__]:
                    apps.append(app)

        return apps

    @classmethod
    def get_plugin(cls, path, plugin_classes, default=None, force_reload=False):
        apps = cls.import_plugin(path, plugin_classes, force_reload)
        if not apps:
            return default

        return apps[0]


if __name__ == "__main__":
    print(PluginManager.get_plugin("auth.database", ["AuthPlugin"]))
    plugins = PluginManager("StepmaniaPlugin", ["example"], "plugins", "plugin")
    plugins.load()
    print(plugins)
    plugins.init("a")
    print(plugins)

    print(PluginManager("StepmaniaController", None, "smserver.controllers"))
    print(PluginManager("ChatPlugin", None, "smserver.chat_commands"))
