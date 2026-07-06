""" Stepmania command module.

This module provide all the command available for stepmania packet
"""

from enum import Enum

class ParentCommand(Enum):
    """ Enum class with can be inherited.

    It allow to group Enumerable in the came category
    """

    @classmethod
    def get(cls, value, default=None):
        """ Search for a value in this Enum and his children """
        try:
            return cls(value)
        except ValueError:
            pass

        for klass in cls.__subclasses__(): #pylint: disable=maybe-no-member
            try:
                return klass(value)
            except ValueError:
                pass

        return default

class SMCommand:
    """ Base class for Stepmania commands - provides lookup method """
    pass

class SMClientCommand(ParentCommand):
    """ List of client commands available """

    NSCPing      = 0
    NSCPingR     = 1
    NSCHello     = 2
    NSCGSR       = 3
    NSCGON       = 4
    NSCGSU       = 5
    NSCSU        = 6
    NSCCM        = 7
    NSCRSG       = 8
    NSCCUUL      = 9
    NSSCSMS      = 10
    NSCUOpts     = 11
    NSSMONL      = 12
    NSCFormatted = 13
    NSCAttack    = 14
    XMLPacket    = 15

class SMServerCommand(ParentCommand):
    """ List of server commands available """

    NSCPing      = 128
    NSCPingR     = 129
    NSCHello     = 130
    NSCGSR       = 131
    NSCGON       = 132
    NSCGSU       = 133
    NSCSU        = 134
    NSCCM        = 135
    NSCRSG       = 136
    NSCCUUL      = 137
    NSSCSMS      = 138
    NSCUOpts     = 139
    NSSMONL      = 140
    NSCFormatted = 141
    NSCAttack    = 142
    XMLPacket    = 143

# Add get method to SMCommand to search in both client and server commands
SMCommand.get = staticmethod(lambda value, default=None:
    SMClientCommand.get(value) or SMServerCommand.get(value) or default
)

class SMOCommand:
    """ Base class for Stepmania Online commands """
    pass

class SMOClientCommand(ParentCommand):
    """ List of SMO Client commands available """

    LOGIN      = 0
    ENTERROOM  = 1
    CREATEROOM = 2
    ROOMINFO   = 3

class SMOServerCommand(ParentCommand):
    """ List of SMO Server commands available """

    LOGIN       = 0
    ROOMUPDATE  = 1
    GENERALINFO = 2
    ROOMINFO    = 3

# Add get method to SMOCommand to search in both client and server commands
SMOCommand.get = staticmethod(lambda value, default=None:
    SMOClientCommand.get(value) or SMOServerCommand.get(value) or default
)