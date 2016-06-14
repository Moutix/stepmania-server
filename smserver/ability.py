#!/usr/bin/env python3
# -*- coding: utf8 -*-

from enum import Enum

class Permissions(Enum):
    create_room = 1
    enter_room = 1
    chat = 1
    change_room_motd = 2

class Ability(object):
    @staticmethod
    def can(action, level=0):
        return level >= action.value

    @staticmethod
    def cannot(action, level=0):
        return level < action.value
