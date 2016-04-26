#!/usr/bin/env python3
# -*- coding: utf8 -*-

class AuthPlugin(object):
    def __init__(self, autocreate):
        self.autocreate = autocreate

    def login(self, user, password):
        return True
