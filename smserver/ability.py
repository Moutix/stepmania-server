#!/usr/bin/env python3
# -*- coding: utf8 -*-

from enum import Enum

class Permissions(Enum):
    create_room = 1
    chat = 1

class Ability(object):
    @staticmethod
    def can(action, level=0):
        return action.value >= level

    @staticmethod
    def cannot(action, level=0):
        return action.value < level
