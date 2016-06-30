#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
    This module add the class needed for creating custom chat command

    :Example:

    Here's a simple ChatPlugin which will send a HelloWorld on use

    ``
    ChatHelloWorld(ChatPlugin):
        helper = "Display Hello World"
        cimmand

        def __call__(self, serv, message):
            serv.send_message("Hello world", to="me")
    ``
"""


class ChatPlugin(object):
    """
        Inherit from this class to add a command in the chat.

        helper: Text that will be show when calling the help command
        permission: Permission needed for this command (see ability)
        room: Specify here if the command need to be execute in a room
        command: The command to use to call this function
    """

    helper = ""
    permission = None
    room = False
    command = None

    def can(self, serv):
        """
            Method call each time somenone try to run this command

            :param serv: The StepmaniaController instance
            :type serv: StepmaniaController
            :return: True if authorize False if not
            :rtype: bool
        """

        if self.room and not serv.room:
            return False

        if self.permission and serv.cannot(self.permission, serv.conn.room):
            return False

        return True

    def __call__(self, serv, message):
        """
            Action to perform when using the command

            :param serv: The StepmaniaController instance
            :param message: The text after the command. (Eg. /command text)
            :type serv: StepmaniaController
            :type message: str
            :return: Nothing
        """

