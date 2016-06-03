#!/usr/bin/env python3
# -*- coding: utf8 -*-

from enum import Enum

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
    LOGIN      = 0
    ENTERROOM  = 1
    CREATEROOM = 2
    ROOMINFO   = 3

class SMOServerCommand(SMOCommand):
    LOGIN       = 0
    ROOMUPDATE  = 1
    GENERALINFO = 2
    ROOMINFO    = 3


class SMPayloadTypeAbstract(object):
    @staticmethod
    def encode(data, opt=None):
        return b''

    @staticmethod
    def decode(payload, opt=None):
        return payload, None

class SMPayloadTypeINT(SMPayloadTypeAbstract):
    @staticmethod
    def encode(data, opt=None):
        if not data:
            data = 0

        if not opt:
            opt = 1

        return data.to_bytes(opt, byteorder='big')

    @staticmethod
    def decode(payload, opt=None):
        if not opt:
            opt = 1

        return payload[opt:], int.from_bytes(payload[:opt], byteorder='big')

class SMPayloadTypeINTLIST(SMPayloadTypeAbstract):
    @staticmethod
    def encode(data, opt=None):
        if not data:
            data = []

        if not opt or len(opt) != 2:
            opt = (1, 1)

        if len(data) < opt[1]:
            data.extend([0 for _ in range(opt[1] - len(data))])

        return b''.join(d.to_bytes(opt[0], byteorder='big') for d in data)

    @staticmethod
    def decode(payload, opt=None):
        if not opt or len(opt) != 2:
            opt = (1, 1)

        return payload[opt[0]*opt[1]:], [int.from_bytes(payload[i:i+opt[0]], byteorder='big')
                                         for i in range(0, opt[0]*opt[1], opt[0])]

class SMPayloadTypeNT(SMPayloadTypeAbstract):
    @staticmethod
    def encode(data, opt=None):
        if not data:
            return b'\x00'
        return data.replace('\x00', '').encode('utf-8') + b'\x00'

    @staticmethod
    def decode(payload, opt=None):
        tmp = payload.split(b'\x00', 1)
        if len(tmp) < 2:
            return payload, None
        return tmp[1], tmp[0].decode('utf-8')

class SMPayloadTypeNTLIST(SMPayloadTypeAbstract):
    @staticmethod
    def encode(data, opt=None):
        if not data:
            return b'\x00'*opt if opt else b'\x00'

        if opt and len(data) < opt:
            data.extend(['' for _ in range(opt - len(data))])

        return b'\x00'.join([d.replace('\x00', '').encode('utf-8') for d in data]) + b'\x00'

    @staticmethod
    def decode(payload, opt=None):
        if opt:
            tmp = payload.split(b'\x00', opt)
        else:
            tmp = payload.split(b'\x00')

        if not tmp:
            return payload, None

        return tmp[-1], [t.decode('utf-8') for t in tmp[:-1]]

class SMPayloadTypeLIST(SMPayloadTypeAbstract):
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
    _command_type = SMCommand
    _command = None
    _payload = []

    def __init__(self, **kwargs):
        self.command = self._command
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
        klasses = [klass for klass in cls.__subclasses__() if klass._command == command]
        if not klasses:
            return None

        return klasses[0](**kwargs)

    @classmethod
    def get_class(cls, command):
        klasses = [klass for klass in cls.__subclasses__() if klass._command == command]
        if not klasses:
            return None

        return klasses[0]

    @property
    def binarycommand(self):
        return self.command.value.to_bytes(1, byteorder='big')

    @property
    def binarysize(self):
        return len(self).to_bytes(4, byteorder='big')

    @property
    def data(self):
        return self.binarycommand + self.payload

    @property
    def binary(self):
        return self.binarysize + self.data

    @property
    def payload(self):
        return self.encode(self.opts, self._payload)

    @classmethod
    def from_payload(cls, payload):
        return cls(**cls.decode(payload, cls._payload)[1])

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
    _command = SMOClientCommand.LOGIN
    _payload = [
        (SMPayloadType.INT, "player_number", None),
        (SMPayloadType.INT, "encryption", None),
        (SMPayloadType.NT, "username", None),
        (SMPayloadType.NT, "password", None)
    ]

class SMOPacketClientEnterRoom(SMOPacketClient):
    _command = SMOClientCommand.ENTERROOM
    _payload = [
        (SMPayloadType.INT, "enter", None),
        (SMPayloadType.NT, "room", None),
        (SMPayloadType.NT, "password", None)
    ]

class SMOPacketClientCreateRoom(SMOPacketClient):
    _command = SMOClientCommand.CREATEROOM
    _payload = [
        (SMPayloadType.INT, "type", None),
        (SMPayloadType.NT, "title", None),
        (SMPayloadType.NT, "description", None),
        (SMPayloadType.NT, "password", None)
    ]

class SMOPacketClientRoomInfo(SMOPacketClient):
    _command = SMOClientCommand.ROOMINFO
    _payload = [
        (SMPayloadType.NT, "room", None)
    ]

class SMOPacketServerLogin(SMOPacketServer):
    _command = SMOServerCommand.LOGIN
    _payload = [
        (SMPayloadType.INT, "approval", None),
        (SMPayloadType.NT, "text", None)
    ]

class SMOPacketServerRoomUpdate(SMOPacketServer):
    _command = SMOServerCommand.ROOMUPDATE
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
    _command = SMOServerCommand.GENERALINFO
    _payload = [
        (SMPayloadType.INT, "format", None),
    ]

class SMOPacketServerRoomInfo(SMOPacketServer):
    _command = SMOServerCommand.ROOMINFO
    _payload = [
        (SMPayloadType.NT, "song_title", None),
        (SMPayloadType.NT, "song_subtitle", None),
        (SMPayloadType.NT, "song_artist", None),
        (SMPayloadType.INT, "num_players", None),
        (SMPayloadType.INT, "max_players", None),
        (SMPayloadType.NTLIST, "players", "num_players"),
    ]

class SMPacketClientNSCPing(SMPacket):
    """ This command will cause server to respond with a PingR Command """

    _command = SMClientCommand.NSCPing
    _payload = []


class SMPacketClientNSCPingR(SMPacket):
    """ This command is used to respond to Ping Command. """

    _command = SMClientCommand.NSCPingR
    _payload = []


class SMPacketClientNSCHello(SMPacket):
    """ This is the first packet from a client to server """

    _command = SMClientCommand.NSCHello
    _payload = [
        (SMPayloadType.INT, "version", None),
        (SMPayloadType.NT, "name", None)
    ]

class SMPacketClientNSCGSR(SMPacket):
    """ Game Start Request:
        This command is called once after most loading is done, and again
        immediately before the sound starts. """

    _command = SMClientCommand.NSCGSR
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
    """ Game Over Notice:
        This command is sent when end of game is encounterd """

    _command = SMClientCommand.NSCGON

class SMPacketClientNSCGSU(SMPacket):
    """ Game Status update:
        Updates game info for each step """

    _command = SMClientCommand.NSCGSU
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
    """ Style Update:
    This is sent when a style is chosen. """

    _command = SMClientCommand.NSCSU
    _payload = [
        (SMPayloadType.INT, "nb_players", None),
        (SMPayloadType.INT, "player_id", None),
        (SMPayloadType.NT, "player_name", None),
    ]

class SMPacketClientNSCCM(SMPacket):
    """ Chat Message
    The user typed a message for general chat. """

    _command = SMClientCommand.NSCCM
    _payload = [
        (SMPayloadType.NT, "message", None),
    ]

class SMPacketClientNSCRSG(SMPacket):
    """ Request Start Game and Tell server existance/non existance of song:
        The user selected a song on a Net-enabled selection """

    _command = SMClientCommand.NSCRSG
    _payload = [
        (SMPayloadType.INT, "usage", 1),
        (SMPayloadType.NT, "song_title", None),
        (SMPayloadType.NT, "song_artist", None),
        (SMPayloadType.NT, "song_subtitle", None),
    ]


class SMPacketClientNSCCUUL(SMPacket):
    """ Reserved """
    _command = SMClientCommand.NSCCUUL

class SMPacketClientNSSCSMS(SMPacket):
    """ User entered/exited Network Music Selection Screen """

    _command = SMClientCommand.NSSCSMS
    _payload = [
        (SMPayloadType.INT, "action", None),
    ]

class SMPacketClientNSCUOpts(SMPacket):
    """ User has changed player options """

    _command = SMClientCommand.NSCUOpts
    _payload = [
        (SMPayloadType.NT, "player_0", None),
        (SMPayloadType.NT, "player_1", None),
    ]


class SMPacketClientNSSMONL(SMPacket):
    """ SMOnline Packet.
    The SMLan packet 12 is a wrapper for the SMOnline packet. """

    _command = SMClientCommand.NSSMONL
    _payload = [
        (SMPayloadType.PACKET, "packet", SMOPacketClient)
    ]

class SMPacketClientNSCFormatted(SMPacket):
    """ Reserved """

    _command = SMClientCommand.NSCFormatted

class SMPacketClientNSCAttack(SMPacket):
    """ Reserved """

    _command = SMClientCommand.NSCAttack

class SMPacketClientXMLPacket(SMPacket):
    """ XMLPacket
    This packet contains data in XML format. """

    _command = SMClientCommand.XMLPacket
    _payload = [
        (SMPayloadType.NT, "xml", None),
    ]

class SMPacketServerNSCPing(SMPacket):
    """ This command will cause server to respond with a PingR Command """

    _command = SMServerCommand.NSCPing

class SMPacketServerNSCPingR(SMPacket):
    """ This command is used to respond to a no operation."""

    _command = SMServerCommand.NSCPingR

class SMPacketServerNSCHello(SMPacket):
    """ This introduces the server. """

    _command = SMServerCommand.NSCHello
    _payload = [
        (SMPayloadType.INT, "version", None),
        (SMPayloadType.NT, "name", None),
        (SMPayloadType.INT, "key", 4)
    ]

class SMPacketServerNSCGSR(SMPacket):
    """ Allow start:
    This will cause the client to start the game."""

    _command = SMServerCommand.NSCGSR

class SMPacketServerNSCGON(SMPacket):
    """ Game over stats
    This packet is send in response to the game over packet
    it contains information regarding how well each player did. """

    _command = SMServerCommand.NSCGON
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
    """ Scoreboard update
    This will update the client's scoreboard. """

    _command = SMServerCommand.NSCGSU
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
    """ System Message
    Send system message to user """

    _command = SMServerCommand.NSCSU
    _payload = [
        (SMPayloadType.NT, "message", None)
    ]

class SMPacketServerNSCCM(SMPacket):
    """ Chat Message
    Add a chat message to the chat window on some StepMania screens. """

    _command = SMServerCommand.NSCCM
    _payload = [
        (SMPayloadType.NT, "message", None)
    ]


class SMPacketServerNSCRSG(SMPacket):
    """ Tell client to start song/ask if client has song
    The user selected a song on a Net-enabled selection """

    _command = SMServerCommand.NSCRSG
    _payload = [
        (SMPayloadType.INT, "usage", 1),
        (SMPayloadType.NT, "song_title", None),
        (SMPayloadType.NT, "song_artist", None),
        (SMPayloadType.NT, "song_subtitle", None),
    ]


class SMPacketServerNSCCUUL(SMPacket):
    """ Update user list
    This sends all the users currently connected """

    _command = SMServerCommand.NSCCUUL
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
    """ Force change to Networking select music screen. """

    _command = SMServerCommand.NSSCSMS
    _payload = [
        (SMPayloadType.NT, "gametype", None),
        (SMPayloadType.NT, "style", None),
    ]


class SMPacketServerNSCUOpts(SMPacket):
    """ Reserved """
    _command = SMServerCommand.NSCUOpts

class SMPacketServerNSSMONL(SMPacket):
    """ SMOnline Packet
    The SMLan packet 12 is a wrapper for the SMOnline packet. """

    _command = SMServerCommand.NSSMONL
    _payload = [
        (SMPayloadType.PACKET, "packet", SMOPacketServer)
    ]

class SMPacketServerNSCFormatted(SMPacket):
    """ Formatted information packet
    Send formatted information regarding the server back to the player."""

    _command = SMServerCommand.NSCFormatted
    _payload = [
        (SMPayloadType.NT, "server_name", None),
        (SMPayloadType.INT, "server_port", 2),
        (SMPayloadType.INT, "nb_players", 2),
    ]


class SMPacketServerNSCAttack(SMPacket):
    """ Attack Client """

    _command = SMServerCommand.NSCAttack
    _payload = [
        (SMPayloadType.INT, "player", 1),
        (SMPayloadType.INT, "time", 4),
        (SMPayloadType.NT, "message", None),
    ]


class SMPacketServerXMLPacket(SMPacket):
    """ XML Reply """

    _command = SMServerCommand.XMLPacket
    _payload = [
        (SMPayloadType.NT, "xml", None),
    ]


def main():
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

if __name__ == "__main__":
    main()
