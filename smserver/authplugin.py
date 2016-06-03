#!/usr/bin/env python3
# -*- coding: utf8 -*-

class AuthPlugin(object):
    def __init__(self, server, autocreate):
        self.server = server
        self.autocreate = autocreate

    def login(self, user, password):
        return True
