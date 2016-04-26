#!/usr/bin/env python3
# -*- coding: utf8 -*-

import inspect

class PluginError(Exception):
    pass

class PluginManager(dict):
    def __init__(self, plugin_class, paths=None, directory=None, plugin_file=None):
        self.plugin_class = plugin_class
        self.plugin_file = plugin_file
        self.directory = directory
        if not paths:
            paths = []
        self.paths = paths

        self._get_plugins

    def _get_plugins(self, paths, force_reload=False):
        for path in paths:
            fullpath = '.'.join([p for p in (self.directory, path, self.plugin_file) if p is not None])
            self[path] = self.import_plugin(fullpath,
                                            plugin_class=self.plugin_class,
                                            force_reload=force_reload)

    @staticmethod
    def import_plugin(path, plugin_class, force_reload=False, default=None):
        module = __import__(path, fromlist=[plugin_class])
        if force_reload:
            reload(module)

        for cls in inspect.getmembers(module, inspect.isclass):
            app = getattr(module, cls[0])
            if app and (app.__name__ == plugin_class or
                        plugin_class in [x.__name__ for x in app.__bases__]):
                return app

        return default


if __name__ == "__main__":
    print(PluginManager.import_plugin("auth.database", "AuthPlugin"))

