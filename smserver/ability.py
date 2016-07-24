#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
    The Ability module provide helper for checking the permission
"""

from enum import Enum

class Permissions(Enum):
    """
        List of available permissions

        The value of each member is the level required for the given action
    """


    create_room = 1
    delete_room = 10
    enter_room = 1
    chat = 1
    change_room_settings = 5
    ban_user = 5
    kick_user = 5
    unban_user = 5
    set_op = 5
    set_owner = 10
    set_voice = 5
    start_game = 5

class Ability(object):
    """
        The Ablitity class provide easy method for checking if someone can
        do a given action
    """

    @staticmethod
    def can(action, level=0):
        """
            Return true if the action is possible with the given level

            :param action: Action to test
            :param int level: Level for this action
            :type action: Permissions
        """

        return level >= action.value

    @staticmethod
    def cannot(action, level=0):
        """
            Return true if the action is not possible with the given level

            :param action: Action to test
            :param int level: Level for this action
            :type action: Permissions
        """

        return level < action.value
