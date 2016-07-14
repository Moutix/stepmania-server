#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
    The ```SMpacket`` module
    ========================

    Provide easy utilisation of the stepmania protocol.

    :Example:
    >>> from smserver.smutils.smpacket import *

    >>> # Create a new packet instance
    >>> packet = SMPacket.new(SMServerCommand.NSCCM, message="test")
    >>> print(packet)
    <SMPacketServerNSCCM message="test">

    >>> # Binary encode your packet
    >>> packet.binary
    b'\\x00\\x00\\x00\\x06\\x87test\\x00'

    >>> # Decode binary data
    >>> packet2 = SMPacket.from_("binary", packet.binary)
    >>> print(packet2)
    <SMPacketServerNSCCM message="test">

    >>> packet = SMPacket.new(SMServerCommand.NSCPing)

    >>> # JSON encode your packet
    >>> packet.json
    '{"_command": 128}'

    >>> # Decode JSON data
    >>> packet2 = SMPacket.from_("json", packet.json)
    >>> print(packet2)
    <SMPacketServerNSCPing >

"""

from enum import Enum
import json

class ParentCommand(Enum):
    @classmethod
    def get(cls, value, default=None):
        try:
            return cls(value)
        except ValueError:
            pass

        for klass in cls.__subclasses__():
            try:
                return klass(value)
            except ValueError:
                pass

        return default

class SMCommand(ParentCommand):
    pass

class SMClientCommand(SMCommand):
    """
        List of client commands available
    """

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

class SMServerCommand(SMCommand):
    """
        List of server commands available
    """

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

class SMOCommand(ParentCommand):
    pass

class SMOClientCommand(SMOCommand):
    """
        List of SMO Client commands available
    """

    LOGIN      = 0
    ENTERROOM  = 1
    CREATEROOM = 2
    ROOMINFO   = 3

class SMOServerCommand(SMOCommand):
    """
        List of SMO Server commands available
    """

    LOGIN       = 0
    ROOMUPDATE  = 1
    GENERALINFO = 2
    ROOMINFO    = 3


class SMPayloadTypeAbstract(object):
    """
        Parent class for declaring new type of data.
    """

    DEFAULT = None

    @staticmethod
    def encode(data, opt=None):
        """
            Define here how the data is encoded.

            Take the data and option and return the encoded data
        """

        return b''

    @staticmethod
    def decode(payload, opt=None):
        """
            Define here how the data is dedoced.

            Take the payload and option and return the data and remaining payload
        """


        return payload, None

class SMPayloadTypeINT(SMPayloadTypeAbstract):
    """
        INT data encode in x bytes.
    """

    DEFAULT = 0

    @staticmethod
    def encode(data, size=1):
        """
            Encode integer into binary string

            :Example:

            >>> SMPayloadTypeINT.encode(2, size=2)
            b'\\x00\\x02'

            >>> SMPayloadTypeINT.encode(123456789, size=4)
            b'\\x07[\\xcd\\x15'

            >>> # Return the max is size exceed
            >>> SMPayloadTypeINT.encode(5165165, size=2)
            b'\\xff\\xff'

        """

        if not data:
            data = 0

        if not size:
            size = 1

        max_size = 2**(size * 8)

        if data >= max_size:
            data = max_size - 1

        return data.to_bytes(size, byteorder='big')

    @staticmethod
    def decode(payload, size=1):
        """
            Decode binary string into integer

            :Example:

            >>> SMPayloadTypeINT.decode(b"\x01remaining_payload", size=1)
            (b'remaining_payload', 1)

            >>> # Return None if size exceed
            >>> SMPayloadTypeINT.decode(b"\x01", size=50)
            (b'\\x01', None)

        """

        if not size:
            size = 1

        if len(payload) < size:
            return payload, None

        return payload[size:], int.from_bytes(payload[:size], byteorder='big')

class SMPayloadTypeINTLIST(SMPayloadTypeAbstract):
    """
        List of integer
    """

    DEFAULT = []

    @staticmethod
    def encode(data, opt=None):
        """
            Encode integer list into binary string.

            :param data: the list to encode
            :param opt: the encoding option: (integer size, size of the array)

            :Example:

            >>> SMPayloadTypeINTLIST.encode([2, 5], opt=(1, 2))
            b'\\x02\\x05'

            >>> SMPayloadTypeINTLIST.encode([1], opt=(1, 2)) # zero padding
            b'\\x01\\x00'

            >>> # Size exceed
            >>> SMPayloadTypeINTLIST.encode([65000, 123456789], opt=(2, 2))
            b'\\xfd\\xe8\\xff\\xff'
        """


        if not data:
            data = []

        if not opt or len(opt) != 2:
            opt = (1, 1)

        if len(data) < opt[1]:
            data.extend([0 for _ in range(opt[1] - len(data))])

        return b''.join(SMPayloadTypeINT.encode(d, opt[0]) for d in data)

    @staticmethod
    def decode(payload, opt=None):
        """
            Decode binary string into int list

            :param data: the string to decode
            :param opt: the encoding option: (integer size, size of the array)

            :Example:

            >>> SMPayloadTypeINTLIST.decode(b"\x02\x05", opt=(1, 2))
            (b'', [2, 5])

            >>> SMPayloadTypeINTLIST.decode(b"\x02\x05remaining_payload", opt=(2, 1))
            (b'remaining_payload', [517])

            >>> # Return none if size exceed
            >>> SMPayloadTypeINTLIST.decode(b'\x01', opt=(1, 5))
            (b'\\x01', None)
        """

        if not opt or len(opt) != 2:
            opt = (1, 1)

        if len(payload) < opt[0]*opt[1]:
            return payload, None

        return payload[opt[0]*opt[1]:], [int.from_bytes(payload[i:i+opt[0]], byteorder='big')
                                         for i in range(0, opt[0]*opt[1], opt[0])]

class SMPayloadTypeNT(SMPayloadTypeAbstract):
    """
        Null terminated string.
    """

    DEFAULT = ""

    @staticmethod
    def encode(data, opt=None):
        """
            Encode unicode string into null terminated string.

            :param data: the string to encode
            :param opt: Do nothing

            :Example:

            >>> SMPayloadTypeNT.encode("unicode_string")
            b'unicode_string\\x00'
        """

        if not data:
            return b'\x00'

        return data.replace('\x00', '').encode('utf-8') + b'\x00'

    @staticmethod
    def decode(payload, opt=None):
        """
            Decode null terminated string into unicode string

            :param data: the null terminated string
            :param opt: Do nothing

            :Example:

            >>> SMPayloadTypeNT.decode(b"nt_string\\x00remaining_string...")
            (b'remaining_string...', 'nt_string')

        """


        tmp = payload.split(b'\x00', 1)
        if len(tmp) < 2:
            return payload, None

        return tmp[1], tmp[0].decode('utf-8')

class SMPayloadTypeNTLIST(SMPayloadTypeAbstract):
    """
        List of null terminated string
    """

    DEFAULT = []

    @staticmethod
    def encode(data, size=None):
        """
            Encode list of unicode string into null terminated strings.

            :param data: the list to encode
            :param size: Size of the list

            :Example:

            >>> SMPayloadTypeNTLIST.encode(["string1", "string2"], 2)
            b'string1\\x00string2\\x00'

            >>> # zero padding
            >>> SMPayloadTypeNTLIST.encode(["string1", "string2"], 5)
            b'string1\\x00string2\\x00\\x00\\x00\\x00'

            >>> # force size
            >>> SMPayloadTypeNTLIST.encode(["string1", "string2"], 1)
            b'string1\\x00'

            >>> # guess size
            >>> SMPayloadTypeNTLIST.encode(["string1", "string2"])
            b'string1\\x00string2\\x00'

        """

        if not data:
            return b'\x00'*size if size else b'\x00'

        if size and len(data) < size:
            data.extend(['' for _ in range(size - len(data))])

        if size and len(data) > size:
            data = data[:size]

        return b'\x00'.join([d.replace('\x00', '').encode('utf-8') for d in data]) + b'\x00'

    @staticmethod
    def decode(payload, size=None):
        """
            Decode byte strings into list of unicode string

            :param data: List of unicode string
            :param size: size of the list

            :Example:

            >>> SMPayloadTypeNTLIST.decode(b"string1\\x00string2\\x00remaining\\x00_string...", 2)
            (b'remaining\\x00_string...', ['string1', 'string2'])

            >>> SMPayloadTypeNTLIST.decode(b"string1\\x00string2\\x00remaining_string...") # guess size
            (b'remaining_string...', ['string1', 'string2'])

            >>> SMPayloadTypeNTLIST.decode(b"string1\\x00remaining_string...", 3)
            (b'remaining_string...', ['string1', '', ''])


        """

        if size:
            tmp = payload.split(b'\x00', size)
        else:
            tmp = payload.split(b'\x00')

        remaining_payload = tmp.pop()

        if size and len(tmp) < size:
            tmp.extend([b'' for _ in range(size - len(tmp))])

        if not tmp:
            return payload, None

        return remaining_payload, [t.decode('utf-8') for t in tmp]

class SMPayloadTypeLIST(SMPayloadTypeAbstract):
    """
        Generic type for declaring list of other type
    """

    DEFAULT = []

    @staticmethod
    def encode(data, opt=None):
        if not data:
            data = []

        if not opt:
            opt = [1, []]

        if len(data) < opt[0]:
            data.extend([{} for _ in range(opt[0] - len(data))])

        return b''.join(SMPacket.encode(d, opt[1]) for d in data)

    @staticmethod
    def decode(payload, opt=None):
        if not opt:
            opt = [1, []]

        res = []
        for _ in range(0, opt[0]):
            payload, tmp = SMPacket.decode(payload, opt[1])
            res.append(tmp)

        return payload, res

class SMPayloadTypeMAP(SMPayloadTypeAbstract):
    """
        Generic type for declaring encoding which depends on precedent values.
    """

    DEFAULT = {}

    @staticmethod
    def encode(data, opt=None):
        if not opt:
            opt = [0, {}]

        size, _, sizeopt = opt[1].get(opt[0], (None, None, None))
        if not size:
            return b''

        return size.value.encode(data, sizeopt)

    @staticmethod
    def decode(payload, opt=None):
        if not opt:
            opt = [0, {}]

        size, _, sizeopt = opt[1].get(opt[0], (None, None, None))
        if not size:
            return payload, None

        return size.value.decode(payload, sizeopt)

class SMPayloadTypePacket(SMPayloadTypeAbstract):
    """
        Type for encoding packet in packet
    """

    @staticmethod
    def encode(data, opt=None):
        if not data:
            return b''

        return data.data

    @staticmethod
    def decode(payload, opt=None):
        if not opt:
            opt = SMPacket

        tmp = opt.parse_data(payload)
        if not tmp:
            return payload, None

        return payload[len(tmp.payload):], tmp


class SMPayloadType(Enum):
    """
        List of the available type
    """

    MSN = 1
    LSN = 2
    NT = SMPayloadTypeNT
    NTLIST = SMPayloadTypeNTLIST
    PACKET = SMPayloadTypePacket
    INT = SMPayloadTypeINT
    INTLIST = SMPayloadTypeINTLIST
    LIST = SMPayloadTypeLIST
    MAP = SMPayloadTypeMAP

class SMPacket(object):
    """
        Main class for declare/parse packet
    """

    _command_type = SMCommand
    _payload = []
    command = None

    def __init__(self, **kwargs):
        self.command = self.command
        if "_command" in kwargs:
            kwargs.pop("_command")

        self.opts = kwargs

    def __len__(self):
        return 1 + len(self.payload)

    def __str__(self):
        return "<%s %s>" % (
            self.__class__.__name__,
            " ".join(['%s="%s"' % (k, v) for k, v in self.opts.items()]))

    def __repr__(self):
        return "<%s %s>" % (
            self.__class__.__name__,
            " ".join(['%s="%s"' % (k, v) for k, v in self.opts.items()]))

    def __getitem__(self, value):
        return self.opts[value]

    def __setitem__(self, key, value):
        self.opts[key] = value

    def get(self, value, default=None):
        return self.opts.get(value, default)

    @classmethod
    def new(cls, command, **kwargs):
        """
            Return an instance with the corresponding command.

            If no command is found, return None

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> print(SMPacket.new(SMServerCommand.NSCCM, message="msg"))
            <SMPacketServerNSCCM message="msg">
        """

        klasses = [klass for klass in cls.__subclasses__() if klass.command == command]
        if not klasses:
            return None

        return klasses[0](**kwargs)

    @classmethod
    def get_class(cls, command):
        """
            Get the class which avec the corresponding command

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> print(SMPacket.get_class(SMServerCommand.NSCCM))
            <class 'smserver.smutils.smpacket.SMPacketServerNSCCM'>
        """

        klasses = [klass for klass in cls.__subclasses__() if klass.command == command]
        if not klasses:
            return None

        return klasses[0]

    @property
    def binarycommand(self):
        """
            Return the command in a binary string

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> packet = SMPacket.new(SMServerCommand.NSCCM, message="msg")
            >>> print(packet.binarycommand)
            b'\\x87'
        """

        return self.command.value.to_bytes(1, byteorder='big')

    @property
    def binarysize(self):
        """
            Return the size of the packet in a 4 bytes string.

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> packet = SMPacket.new(SMServerCommand.NSCCM, message="msg")
            >>> print(packet.binarysize)
            b'\\x00\\x00\\x00\\x05'
        """

        return len(self).to_bytes(4, byteorder='big')

    @property
    def data(self):
        """
            Return the command + payload in a binary string

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> packet = SMPacket.new(SMServerCommand.NSCCM, message="msg")
            >>> print(packet.data)
            b'\\x87msg\\x00'
        """

        return self.binarycommand + self.payload

    @property
    def binary(self):
        """
            Return the full binary encoded packet (size + command + payload)

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> packet = SMPacket.new(SMServerCommand.NSCCM, message="msg")
            >>> print(packet.binary)
            b'\\x00\\x00\\x00\\x05\\x87msg\\x00'
        """

        return self.binarysize + self.data

    @property
    def payload(self):
        """
            Return the paylaod encoded in binary

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> packet = SMPacket.new(SMServerCommand.NSCCM, message="msg")
            >>> print(packet.payload)
            b'msg\\x00'
        """

        return self.encode(self.opts, self._payload)

    @property
    def json(self):
        """
            Return the JSON encoded packet

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> packet = SMPacket.new(SMServerCommand.NSCPing)
            >>> print(packet.json)
            {"_command": 128}
        """

        data = {}
        data["_command"] = self.command.value
        for opt, value in self.opts.items():
            if issubclass(value.__class__, SMPacket):
                data[opt] = value.json
                continue

            data[opt] = value

        return json.dumps(data)

    @classmethod
    def from_payload(cls, payload):
        """
            Decode the given binary payload

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> payload_data = b'msg\\x00'
            >>> print(SMPacketServerNSCCM.from_payload(payload_data))
            <SMPacketServerNSCCM message="msg">
        """

        return cls(**cls.decode(payload, cls._payload)[1])

    @classmethod
    def from_json(cls, payload):
        """
            Decode a JSON encoded packet

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> json_data = '{"message": "msg"}'
            >>> print(SMPacketServerNSCCM.from_json(json_data))
            <SMPacketServerNSCCM message="msg">
        """

        return cls(**cls.decode_json(payload, cls._payload))

    def to_(self, encoding):
        """
            Encode the packet to the specified format (json or binary)
        """

        return {
            "json": self.json,
            "binary": self.binary
        }[encoding]

    @classmethod
    def from_(cls, encoding, data):
        """
            Decode the packet from the specified format (json or binary)
        """

        return {
            "json": cls.parse_json,
            "binary": cls.parse_binary
        }[encoding](data)

    @classmethod
    def parse_json(cls, data):
        try:
            opts = json.loads(data)
        except ValueError:
            return None

        command = cls._command_type.get(opts.get("_command", -1))
        if not command:
            return None

        return cls.get_class(command).from_json(data)

    @classmethod
    def parse_data(cls, data):
        if not data:
            return None

        command = cls._command_type.get(data[0])
        if not command:
            return None

        return cls.get_class(command).from_payload(data[1:])

    @classmethod
    def parse_binary(cls, binary):
        if len(binary) < 4:
            return None

        return cls.parse_data(binary[4:])

    @classmethod
    def encode(cls, values, payload_option):
        payload = b""
        byte = ""

        for size, name, opt in payload_option:
            if size == SMPayloadType.MSN:
                byte += cls._to_bin_str(values.get(name, 0))
                continue

            if size == SMPayloadType.LSN:
                byte += cls._to_bin_str(values.get(name, 0))
                payload += bytes([int(byte, 2)])
                byte = ""
                continue

            res = size.value.encode(values.get(name), cls._replace_from_options(values, opt))
            if not res:
                continue

            payload += res

        return payload

    @classmethod
    def decode(cls, payload, payload_option):
        opts = {}
        for size, name, opt in payload_option:
            if size == SMPayloadType.MSN:
                opts[name] = int(cls._to_bin_str(payload[0], 8)[:4], 2)
                continue

            if size == SMPayloadType.LSN:
                opts[name] = int(cls._to_bin_str(payload[0], 8)[4:], 2)
                payload = payload[1:]
                continue

            payload, opts[name] = size.value.decode(payload, cls._replace_from_options(opts, opt))

        return payload, opts

    @classmethod
    def decode_json(cls, payload, payload_option):
        opts = json.loads(payload)

        for size, name, opt in payload_option:
            if size == SMPayloadType.PACKET:
                if not opt:
                    opt = SMPacket

                opts[name] = opt.parse_json(opts[name])

            if isinstance(size.value, int):
                default = 0
            else:
                default = size.value.DEFAULT

            if name not in opts:
                opts[name] = default

        return opts

    @classmethod
    def _replace_from_options(cls, options, value):
        if isinstance(value, str):
            return options.get(value, value)

        if isinstance(value, (tuple, list)):
            return [cls._replace_from_options(options, v) for v in value]

        if isinstance(value, dict):
            return dict((k, cls._replace_from_options(options, v)) for k, v in value.items())

        return value

    @staticmethod
    def _to_bin_str(number, size=4):
        number = "{0:b}".format(number)
        if len(number) == size:
            return number

        if len(number) > size:
            return "1"*size

        return "0"*(size-len(number)) + number


class SMOPacketClient(SMPacket):
    _command_type = SMOClientCommand

class SMOPacketServer(SMPacket):
    _command_type = SMOServerCommand

class SMOPacketClientLogin(SMOPacketClient):
    command = SMOClientCommand.LOGIN
    _payload = [
        (SMPayloadType.INT, "player_number", None),
        (SMPayloadType.INT, "encryption", None),
        (SMPayloadType.NT, "username", None),
        (SMPayloadType.NT, "password", None)
    ]

class SMOPacketClientEnterRoom(SMOPacketClient):
    command = SMOClientCommand.ENTERROOM
    _payload = [
        (SMPayloadType.INT, "enter", None),
        (SMPayloadType.NT, "room", None),
        (SMPayloadType.NT, "password", None)
    ]

class SMOPacketClientCreateRoom(SMOPacketClient):
    command = SMOClientCommand.CREATEROOM
    _payload = [
        (SMPayloadType.INT, "type", None),
        (SMPayloadType.NT, "title", None),
        (SMPayloadType.NT, "description", None),
        (SMPayloadType.NT, "password", None)
    ]

class SMOPacketClientRoomInfo(SMOPacketClient):
    command = SMOClientCommand.ROOMINFO
    _payload = [
        (SMPayloadType.NT, "room", None)
    ]

class SMOPacketServerLogin(SMOPacketServer):
    command = SMOServerCommand.LOGIN
    _payload = [
        (SMPayloadType.INT, "approval", None),
        (SMPayloadType.NT, "text", None)
    ]

class SMOPacketServerRoomUpdate(SMOPacketServer):
    command = SMOServerCommand.ROOMUPDATE
    _payload = [
        (SMPayloadType.INT, "type", None),
        (SMPayloadType.MAP, "room_title", ("type", {
            0: (SMPayloadType.NT, None, None),
        })),
        (SMPayloadType.MAP, "room_description", ("type", {
            0: (SMPayloadType.NT, None, None),
        })),
        (SMPayloadType.MAP, "room_type", ("type", {
            0: (SMPayloadType.INT, None, 1),
        })),
        (SMPayloadType.MAP, "subroom", ("type", {
            0: (SMPayloadType.INT, None, 1),
        })),
        (SMPayloadType.MAP, "nb_rooms", ("type", {
            1: (SMPayloadType.INT, None, 1),
        })),
        (SMPayloadType.MAP, "rooms", ("type", {
            1: (SMPayloadType.LIST, None, ("nb_rooms", [
                (SMPayloadType.NT, "title", None),
                (SMPayloadType.NT, "description", None),
            ])),
        })),
        (SMPayloadType.MAP, "room_status", ("type", {
            1: (SMPayloadType.INTLIST, None, (1, "nb_rooms")),
        })),
        (SMPayloadType.MAP, "room_flags", ("type", {
            1: (SMPayloadType.INTLIST, None, (1, "nb_rooms")),
        })),
    ]

class SMOPacketServerGeneralInfo(SMOPacketServer):
    command = SMOServerCommand.GENERALINFO
    _payload = [
        (SMPayloadType.INT, "format", None),
    ]

class SMOPacketServerRoomInfo(SMOPacketServer):
    command = SMOServerCommand.ROOMINFO
    _payload = [
        (SMPayloadType.NT, "song_title", None),
        (SMPayloadType.NT, "song_subtitle", None),
        (SMPayloadType.NT, "song_artist", None),
        (SMPayloadType.INT, "num_players", None),
        (SMPayloadType.INT, "max_players", None),
        (SMPayloadType.NTLIST, "players", "num_players"),
    ]

class SMPacketClientNSCPing(SMPacket):
    """
        Client command 000. (Ping)

        This command will cause server to respond with a PingR Command

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketClientNSCPing()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x00'
    """

    command = SMClientCommand.NSCPing
    _payload = []


class SMPacketClientNSCPingR(SMPacket):
    """
        Client command 001. (Ping response)

        This command is used to respond to Ping Command.

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketClientNSCPingR()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x01'
    """

    command = SMClientCommand.NSCPingR
    _payload = []


class SMPacketClientNSCHello(SMPacket):
    """
        Client command 002. (Hello)

        This is the first packet from a client to server.

        :param int version: Client protocol version
        :param str name: Name of the stepmania build

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketClientNSCHello(
        ...     name="stepmania",
        ...     version=128
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x0c\\x02\\x80stepmania\\x00'
    """

    command = SMClientCommand.NSCHello
    _payload = [
        (SMPayloadType.INT, "version", None),
        (SMPayloadType.NT, "name", None)
    ]

class SMPacketClientNSCGSR(SMPacket):
    """
        Client command 003 (Game Start Request)

        This command is called once after most loading is done, and again
        immediately before the sound starts.

        The server has to respond with a SMPacketServerNSCGSR, if not the
        client will freeze.

        :param int first_player_feet: Primary player feet (0 for no player)
        :param int second_player_feet: Secondary player feet (0 for no player)
        :param int first_player_difficulty: Primary player difficulty (0=Beginner, 1=easy, etc.)
        :param int second_player_difficulty: Secondary player difficulty (0=Beginner, 1=easy, etc.)
        :param int start_position: (0 is pre-sync, 1 is for sync)
        :param int reserved: ignored
        :param str song_title: Title of the song to play
        :param str song_subtitle: Subtitle of the song to play
        :param str song_artist: Artist of the song to play
        :param str course_title: Course Title
        :param str song_options: Song option in string format
        :param str first_player_options: Primary player's option
        :param str second_player_options: Secondary player's option
    """

    command = SMClientCommand.NSCGSR
    _payload = [
        (SMPayloadType.MSN, "first_player_feet", None),
        (SMPayloadType.LSN, "second_player_feet", None),
        (SMPayloadType.MSN, "first_player_difficulty", None),
        (SMPayloadType.LSN, "second_player_difficulty", None),
        (SMPayloadType.MSN, "start_position", None),
        (SMPayloadType.LSN, "reserved", None),
        (SMPayloadType.NT, "song_title", None),
        (SMPayloadType.NT, "song_subtitle", None),
        (SMPayloadType.NT, "song_artist", None),
        (SMPayloadType.NT, "course_title", None),
        (SMPayloadType.NT, "song_options", None),
        (SMPayloadType.NT, "first_player_options", None),
        (SMPayloadType.NT, "second_player_options", None),
    ]


class SMPacketClientNSCGON(SMPacket):
    """
        Client command 004 (Game Over Notice)

        This command is sent when end of game is encounter.

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketClientNSCGON()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x04'
    """

    command = SMClientCommand.NSCGON

class SMPacketClientNSCGSU(SMPacket):
    """
        Client command 005 (Game Status update)

        Update game info for each step in the game

        :param int player_id: player # (0 or 1)
        :param int step_id: (1: hitMine, 2: AvoidMine, ...)
        :param int grade: Projected Grade (0: AAAA, 1: AAA, ...)
        :param int reserved: ignored
        :param int score: Actual score
        :param int combo: Actual combo
        :param int health: Actual health
        :param int offset: Offset from the note (32767=miss)
    """

    command = SMClientCommand.NSCGSU
    _payload = [
        (SMPayloadType.MSN, "player_id", None),
        (SMPayloadType.LSN, "step_id", None),
        (SMPayloadType.MSN, "grade", None),
        (SMPayloadType.LSN, "reserved", None),
        (SMPayloadType.INT, "score", 4),
        (SMPayloadType.INT, "combo", 2),
        (SMPayloadType.INT, "health", 2),
        (SMPayloadType.INT, "offset", 2)
    ]

class SMPacketClientNSCSU(SMPacket):
    """
        Client command 006 (Style Update)

        This is sent when a profile is choosed. It also indicates the number
        of players in the local client. (1 or 2)

        :param int nb_players: Number of players in the client (1 or 2)
        :param int player_id: Player ID (0 or 1)
        :param str player_name: Player name

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketClientNSCSU(
        ...     nb_players=2,
        ...     player_id=0,
        ...     player_name="profile1",
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x0c\\x06\\x02\\x00profile1\\x00'
    """

    command = SMClientCommand.NSCSU
    _payload = [
        (SMPayloadType.INT, "nb_players", None),
        (SMPayloadType.INT, "player_id", None),
        (SMPayloadType.NT, "player_name", None),
    ]

class SMPacketClientNSCCM(SMPacket):
    """
        Client command 007 (Chat Message)

        The user typed a message for general chat.

        :param str message: The message sent by the client.

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketClientNSCCM(message="Client message")
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x10\\x07Client message\\x00'
    """

    command = SMClientCommand.NSCCM
    _payload = [
        (SMPayloadType.NT, "message", None),
    ]

class SMPacketClientNSCRSG(SMPacket):
    """
        Client command 008 (Request Start Game)

        Request Start Game and Tell server existance/non existance of song:
        The user selected a song on a Net-enabled selection

        :param int usage: Usage for this message
        :param str song_title: Song title
        :param str song_subtitle: Song artist
        :param str song_artist: Song subtitle

        :Example:

        >>> # Client select the song ('Title', by 'Artist').
        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketClientNSCRSG(
        ...     usage=2,
        ...     song_title="Title",
        ...     song_artist="Artist",
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x10\\x08\\x02Title\\x00Artist\\x00\\x00'
    """

    command = SMClientCommand.NSCRSG
    _payload = [
        (SMPayloadType.INT, "usage", 1),
        (SMPayloadType.NT, "song_title", None),
        (SMPayloadType.NT, "song_artist", None),
        (SMPayloadType.NT, "song_subtitle", None),
    ]


class SMPacketClientNSCCUUL(SMPacket):
    """
        Client command 009 (reserved)
    """

    command = SMClientCommand.NSCCUUL

class SMPacketClientNSSCSMS(SMPacket):
    """
        Client command 010 (User status)

        Indicate where the user is

        :param int action: Int enum indicating where the user is

        Action available:

        * 0: exited ScreenNetSelectMusic
        * 1: entered ScreenNetSelectMusic
        * 2: Not Sent
        * 3: entered options screen
        * 4: exited the evaluation screen
        * 5: entered evaluation screen
        * 6: exited ScreenNetRoom
        * 7: entered ScreenNetRoom

        :Example:

        >>> from smserver.smutils import smpacket

        >>> # Client enter in room selection
        >>> packet = smpacket.SMPacketClientNSSCSMS(
        ...     action=7,
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x02\\n\\x07'
   """

    command = SMClientCommand.NSSCSMS
    _payload = [
        (SMPayloadType.INT, "action", None),
    ]

class SMPacketClientNSCUOpts(SMPacket):
    """
        Client command 011 (User options)

        User has changed player's options

        :param str player_0: Player 0 options
        :param str player_1: Player 1 options
    """

    command = SMClientCommand.NSCUOpts
    _payload = [
        (SMPayloadType.NT, "player_0", None),
        (SMPayloadType.NT, "player_1", None),
    ]


class SMPacketClientNSSMONL(SMPacket):
    """
        Client command 012 (SMOnline Packet)

        The SMLan packet 12 is a wrapper for the SMOnline packet.

        :param packet: The SMOPacket to include
        :type packet: SMOPacketClient
    """

    command = SMClientCommand.NSSMONL
    _payload = [
        (SMPayloadType.PACKET, "packet", SMOPacketClient)
    ]

class SMPacketClientNSCFormatted(SMPacket):
    """
        Client command 013 (reserved)
    """

    command = SMClientCommand.NSCFormatted

class SMPacketClientNSCAttack(SMPacket):
    """
        Client command 014 (reserved)
    """

    command = SMClientCommand.NSCAttack

class SMPacketClientXMLPacket(SMPacket):
    """
        Client command 15 (XMLPacket)

        This packet contains data in XML format.

        :param str xml: XML string
    """

    command = SMClientCommand.XMLPacket
    _payload = [
        (SMPayloadType.NT, "xml", None),
    ]

class SMPacketServerNSCPing(SMPacket):
    """
        Server command 128 (Ping)

        This command will cause client to respond with a PingR command

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketServerNSCPing()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x80'
    """

    command = SMServerCommand.NSCPing

class SMPacketServerNSCPingR(SMPacket):
    """
        Server command 129 (PingR)

        This command is used to respond to a Ping command.

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketServerNSCPingR()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x81'
    """

    command = SMServerCommand.NSCPingR

class SMPacketServerNSCHello(SMPacket):
    """
        Server command 130 (Hello)

        This command introduces the server. (In response of Client Hello
        command)

        :param str version: The server protocol version (always 128)
        :param str name: Name of the server
        :param int key: Random key, used for hash password

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketServerNSCHello(
        ...     version=128,
        ...     name="MyServer",
        ...     key=999999999
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x0f\\x82\\x80MyServer\\x00;\\x9a\\xc9\\xff'
    """

    command = SMServerCommand.NSCHello
    _payload = [
        (SMPayloadType.INT, "version", None),
        (SMPayloadType.NT, "name", None),
        (SMPayloadType.INT, "key", 4)
    ]

class SMPacketServerNSCGSR(SMPacket):
    """
        Server command 131 (Allow Start)

        This will cause the client to start the game

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketServerNSCGSR()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x83'
    """

    command = SMServerCommand.NSCGSR

class SMPacketServerNSCGON(SMPacket):
    """
        Server command 132 (Game over stats)

        This packet is send in response to the game over packet. It
        contains information regarding how well each player did.

        :param int nb_players: NB of players stats in this packet (size of the next list)
        :param list ids: Player's ID (calculate from the SMPacketServerNSCUUL)
        :param list score: Player's score
        :param list grade: Player's grade
        :param list difficulty: Player's difficulty
        :param list flawless: NB of flawless note
        :param list perfect: NB of perfect note
        :param list great: NB of great note
        :param list good: NB of good note
        :param list bad: NB of bad note
        :param list miss: NB of miss note
        :param list held: NB of held note
        :param list max_combo: Player's max combo
        :param list options: Player's options
    """

    command = SMServerCommand.NSCGON
    _payload = [
        (SMPayloadType.INT, "nb_players", 1),
        (SMPayloadType.INTLIST, "ids", (1, "nb_players")),
        (SMPayloadType.INTLIST, "score", (4, "nb_players")),
        (SMPayloadType.INTLIST, "grade", (1, "nb_players")),
        (SMPayloadType.INTLIST, "difficulty", (1, "nb_players")),
        (SMPayloadType.INTLIST, "flawless", (2, "nb_players")),
        (SMPayloadType.INTLIST, "perfect", (2, "nb_players")),
        (SMPayloadType.INTLIST, "great", (2, "nb_players")),
        (SMPayloadType.INTLIST, "good", (2, "nb_players")),
        (SMPayloadType.INTLIST, "bad", (2, "nb_players")),
        (SMPayloadType.INTLIST, "miss", (2, "nb_players")),
        (SMPayloadType.INTLIST, "held", (2, "nb_players")),
        (SMPayloadType.INTLIST, "max_combo", (2, "nb_players")),
        (SMPayloadType.NTLIST, "options", "nb_players"),
    ]

class SMPacketServerNSCGSU(SMPacket):
    """
        Server command 133 (Scoreboard update)

        This will update the client's scoreboard.

        :param int section: Which section to update (0: names, 1:combos, 2: grades)
        :param int nb_players: Nb of plyaers in this packet
        :param list options: Int list contining names, combos or grades

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketServerNSCGSU(
        ...     section=1, # Update the actual combo
        ...     nb_players=2, # 2 users in this packet
        ...     options=[12, 5] # List containing the combos
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x07\\x85\\x01\\x02\\x00\\x0c\\x00\\x05'
    """

    command = SMServerCommand.NSCGSU
    _payload = [
        (SMPayloadType.INT, "section", 1),
        (SMPayloadType.INT, "nb_players", 1),
        (SMPayloadType.MAP, "options", ("section", {
            0: (SMPayloadType.INTLIST, None, (1, "nb_players")),
            1: (SMPayloadType.INTLIST, None, (2, "nb_players")),
            2: (SMPayloadType.INTLIST, None, (1, "nb_players")),
        }))
    ]

class SMPacketServerNSCSU(SMPacket):
    """
        Server command 134 (System Message)

        Send a system message to user

        :param str message: The message to send

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketServerNSCSU(message="System message")
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x10\\x86System message\\x00'
    """

    command = SMServerCommand.NSCSU
    _payload = [
        (SMPayloadType.NT, "message", None)
    ]

class SMPacketServerNSCCM(SMPacket):
    """
        Server command 135 (Chat Message)

        Add a chat message to the chat window on some StepMania screens.

        :param str message: The message to add

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketServerNSCSU(message="Client message")
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x10\\x86Client message\\x00'
    """

    command = SMServerCommand.NSCCM
    _payload = [
        (SMPayloadType.NT, "message", None)
    ]


class SMPacketServerNSCRSG(SMPacket):
    """
        Server command 136 (Request Start Game)

        Tell client to start song/ask if client has song

        :param int usage: Usage of this message
        :param str song_title: Song title
        :param str song_artist: Song artist
        :param str song_subtitle: Song subtitle

        Usage available:

        * 0: See if client has song
        * 1: See if client has song, if so, scroll to song
        * 2: See if client has song, if so, scroll to song, and play that song
        * 3: Blindly start song

        :Example:

        >>> from smserver.smutils import smpacket
        >>> packet = smpacket.SMPacketServerNSCRSG(
        ...     usage=0, # Check song presence
        ...     song_title="title",
        ...     song_artist="artist",
        ...     song_subtitle="subtitle",
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x18\\x88\\x00title\\x00artist\\x00subtitle\\x00'
    """

    command = SMServerCommand.NSCRSG
    _payload = [
        (SMPayloadType.INT, "usage", 1),
        (SMPayloadType.NT, "song_title", None),
        (SMPayloadType.NT, "song_artist", None),
        (SMPayloadType.NT, "song_subtitle", None),
    ]


class SMPacketServerNSCCUUL(SMPacket):
    """
        Server command 137 (Update user list)

        This sends all the users currently connected

        :param int max_players: NB max of players (max 255)
        :param int nb_players: NB of player's in this packet
        :param list players: List containing status and name for each user
    """

    command = SMServerCommand.NSCCUUL
    _payload = [
        (SMPayloadType.INT, "max_players", 1),
        (SMPayloadType.INT, "nb_players", 1),
        (SMPayloadType.LIST, "players", ("nb_players", [
            (SMPayloadType.INT, "status", 1),
            (SMPayloadType.NT, "name", None),
            ])
        )
    ]

class SMPacketServerNSSCSMS(SMPacket):
    """
        Server command 138

        Force change to Networking select music screen.

        :param str gametype: Set specified gametype
        :param str style: Set specified style
    """

    command = SMServerCommand.NSSCSMS
    _payload = [
        (SMPayloadType.NT, "gametype", None),
        (SMPayloadType.NT, "style", None),
    ]


class SMPacketServerNSCUOpts(SMPacket):
    """
        Server command 139 (reserved)
    """

    command = SMServerCommand.NSCUOpts

class SMPacketServerNSSMONL(SMPacket):
    """
        Server command 140 (SMOnline Packet)

        The SMLan packet 140 is a wrapper for the SMOnline packet.

        :param packet: The SMOPacket to include
        :type packet: SMOPacketServer
    """

    command = SMServerCommand.NSSMONL
    _payload = [
        (SMPayloadType.PACKET, "packet", SMOPacketServer)
    ]

class SMPacketServerNSCFormatted(SMPacket):
    """
        Server command 141 (Formatted information packet)

        Send formatted information regarding the server back to the player.

        :param str server_name: Server name
        :param int server_port: Port the server is listening on
        :param int nb_players: Number of players connected
    """

    command = SMServerCommand.NSCFormatted
    _payload = [
        (SMPayloadType.NT, "server_name", None),
        (SMPayloadType.INT, "server_port", 2),
        (SMPayloadType.INT, "nb_players", 2),
    ]


class SMPacketServerNSCAttack(SMPacket):
    """
        Server command 142 (Attack Client)

        :param int player: Player number (0 or 1)
        :param int time: Duration of the attack (in ms)
        :param attack: Text describing modifiers
        :type attack: str or smserver.smutils.smattack.SMAttack

        List of attack available are in smattack module.

        :Example:

        >>> from smserver.smutils import smpacket, smattack
        >>> packet = smpacket.SMPacketServerNSCAttack(
        ...     player=0, # Send the attack to the player 0
        ...     time=1000, # The attack will last 1 second
        ...     attack='drunk', #Send a drunk attack
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x0c\\x8e\\x00\\x00\\x00\\x03\\xe8drunk\\x00'

        >>> packet = smpacket.SMPacketServerNSCAttack(
        ...     player=0,
        ...     time=1000,
        ...     attack=smattack.SMAttack.Drunk, # Use an Enum value
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x0c\\x8e\\x00\\x00\\x00\\x03\\xe8drunk\\x00'
    """

    def __init__(self, player=0, time=1000, attack=None):
        if not isinstance(attack, str):
            attack = attack.value

        SMPacket.__init__(self, player=player, time=time, attack=attack)

    command = SMServerCommand.NSCAttack
    _payload = [
        (SMPayloadType.INT, "player", 1),
        (SMPayloadType.INT, "time", 4),
        (SMPayloadType.NT, "attack", None),
    ]


class SMPacketServerXMLPacket(SMPacket):
    """
        Server command 143 (XMLPacket)

        This packet contains data in XML format.

        :param str xml: XML string
    """

    command = SMServerCommand.XMLPacket
    _payload = [
        (SMPayloadType.NT, "xml", None),
    ]


def main():
    import doctest
    doctest.testmod()

    packet = SMPacket.new(
        SMClientCommand.NSCGSR,
        second_player_feet=8,
        first_player_feet=12,
        song_title="Wouhou whouhouhou",
        song_subtitle="super sous titer"
    )

    print(packet)
    print(packet.payload)
    assert packet.binary == SMPacket.parse_binary(packet.binary).binary

    packet = SMPacket.new(
        SMServerCommand.NSSMONL,
        packet=SMOPacketServer.new(
            SMOServerCommand.ROOMINFO,
            song_title="song_title",
            num_players=3,
            players=["bidule", "machin", "truc"]
        )
    )

    print(packet)
    print(packet.payload)
    assert packet.binary == SMPacket.parse_binary(packet.binary).binary

    packet = SMPacket.new(
        SMServerCommand.NSCGON,
        nb_players=3,
        ids=[5, 2, 8],
        scores=[1550, 1786, 1632],
    )

    print(packet)
    print(packet.payload)
    assert packet.binary == SMPacket.parse_binary(packet.binary).binary

    packet = SMPacket.new(
        SMServerCommand.NSCCUUL,
        max_players=255,
        nb_players=5,
        players=[{"status": 5, "name": "machin"}, {"status": 1, "name": "bidule"}]
    )

    print(packet)
    print(packet.payload)
    assert packet.binary == SMPacket.parse_binary(packet.binary).binary

    packet = SMPacket.new(
        SMServerCommand.NSCGSU,
        section=1,
        nb_players=3,
        options=[1, 3, 5]
    )

    print(packet)
    print(packet.payload)
    assert packet.binary == SMPacket.parse_binary(packet.binary).binary

    packet = SMPacket.new(
        SMServerCommand.NSSMONL,
        packet=SMOPacketServer.new(
            SMOServerCommand.ROOMUPDATE,
            type=0,
            room_title="Super Room",
            subroom=1,
            room_description="description de la salle",
        )
    )
    print(packet)
    print(packet.payload)
    assert packet.binary == SMPacket.parse_binary(packet.binary).binary

    packet = SMPacket.new(
        SMServerCommand.NSSMONL,
        packet=SMOPacketServer.new(
            SMOServerCommand.ROOMUPDATE,
            type=1,
            nb_rooms=3,
            rooms=[
                {"title": "salle1", "description": "description1"},
                {"title": "salle2", "description": "description2"},
                {"title": "salle3", "description": "description3"},
            ],
            room_description="description de la salle",
        )
    )

    print(packet)
    print(packet.payload)
    assert packet.binary == SMPacket.parse_binary(packet.binary).binary

    assert packet.binary == SMPacket.from_("json", packet.to_("json")).binary

if __name__ == "__main__":
    main()
