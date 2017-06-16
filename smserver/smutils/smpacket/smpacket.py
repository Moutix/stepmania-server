"""
    The ```SMpacket`` module
    ========================

    Provide easy utilisation of the stepmania protocol.

    :Example:
    >>> from smserver.smutils.smpacket import smcommand
    >>> from smserver.smutils.smpacket import smpacket

    >>> # Create a new packet instance
    >>> packet = SMPacket.new(smcommand.SMServerCommand.NSCCM, message="test")
    >>> print(packet)
    <SMPacketServerNSCCM message="test">

    >>> # Binary encode your packet
    >>> packet.binary
    b'\\x00\\x00\\x00\\x06\\x87test\\x00'

    >>> # Decode binary data
    >>> packet2 = SMPacket.from_("binary", packet.binary)
    >>> print(packet2)
    <SMPacketServerNSCCM message="test">

    >>> packet = SMPacket.new(smcommand.SMServerCommand.NSCPing)

    >>> # JSON encode your packet
    >>> packet.json
    '{"_command": 128}'

    >>> # Decode JSON data
    >>> packet2 = SMPacket.from_("json", packet.json)
    >>> print(packet2)
    <SMPacketServerNSCPing >
"""

import json

from smserver.smutils.smpacket import smcommand
from smserver.smutils.smpacket import smencoder

class _SMPacketMetaclass(type):
    """Metaclass that implements PEP 487 protocol"""

    def __init__(cls, name, bases, attrs, **kw):
        super().__init__(name, bases, attrs, **kw)
        parent_class = super(cls, cls)
        if hasattr(parent_class, '__init_subclass_custom__'):
            parent_class.__init_subclass_custom__(cls, **kw)


class SMPacket(metaclass=_SMPacketMetaclass):
    """ Main class for declare/parse packet """

    _command_type = smcommand.SMCommand
    _payload = []
    _subclasses = {}

    command = None

    def __init__(self, **kwargs):
        self.command = self.command
        if "_command" in kwargs:
            kwargs.pop("_command")

        self.opts = kwargs

    def __init_subclass_custom__(cls, **_kwargs): #pylint: disable=no-self-argument
        command = cls.command

        if not command:
            return

        if command in cls._subclasses:
            raise ValueError("Command already defined")

        cls._subclasses[command] = cls

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
            >>> print(SMPacket.new(smcommand.SMServerCommand.NSCCM, message="msg"))
            <SMPacketServerNSCCM message="msg">
        """

        if command not in cls._subclasses:
            return None

        return cls._subclasses[command](**kwargs)

    @classmethod
    def get_class(cls, command):
        """
            Get the class which avec the corresponding command

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> print(SMPacket.get_class(smcommand.SMServerCommand.NSCCM))
            <class 'smserver.smutils.smpacket.smpacket.SMPacketServerNSCCM'>
        """


        return cls._subclasses.get(command, None)

    @property
    def binarycommand(self):
        """
            Return the command in a binary string

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> packet = SMPacket.new(smcommand.SMServerCommand.NSCCM, message="msg")
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
            >>> packet = SMPacket.new(smcommand.SMServerCommand.NSCCM, message="msg")
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
            >>> packet = SMPacket.new(smcommand.SMServerCommand.NSCCM, message="msg")
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
            >>> packet = SMPacket.new(smcommand.SMServerCommand.NSCCM, message="msg")
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
            >>> packet = SMPacket.new(smcommand.SMServerCommand.NSCCM, message="msg")
            >>> print(packet.payload)
            b'msg\\x00'
        """

        return smencoder.BinaryEncoder.encode(self.opts, self._payload)

    @property
    def json(self):
        """
            Return the JSON encoded packet

            :Example:

            >>> from smserver.smutils.smpacket import *
            >>> packet = SMPacket.new(smcommand.SMServerCommand.NSCPing)
            >>> print(packet.json)
            {"_command": 128}
        """

        return smencoder.JSONEncoder.encode(self.opts, self._payload, command=self.command.value)

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

        return cls(
            **smencoder.BinaryEncoder.decode(payload, cls._payload)[1]
        )

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

        return cls(
            **smencoder.JSONEncoder.decode(payload, cls._payload)
        )

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
        """ Parse a JSON packet """
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
        """ Parse a binary packet """

        if not data:
            return None

        command = cls._command_type.get(data[0])
        if not command:
            return None

        return cls.get_class(command).from_payload(data[1:])

    @classmethod
    def parse_binary(cls, binary):
        """ Parse a binary payload """

        if len(binary) < 4:
            return None

        return cls.parse_data(binary[4:])


class SMOPacketClient(SMPacket):
    _command_type = smcommand.SMOClientCommand

class SMOPacketServer(SMPacket):
    _command_type = smcommand.SMOServerCommand

class SMOPacketClientLogin(SMOPacketClient):
    command = smcommand.SMOClientCommand.LOGIN
    _payload = [
        (smencoder.SMPayloadType.INT, "player_number", None),
        (smencoder.SMPayloadType.INT, "encryption", None),
        (smencoder.SMPayloadType.NT, "username", None),
        (smencoder.SMPayloadType.NT, "password", None)
    ]

class SMOPacketClientEnterRoom(SMOPacketClient):
    command = smcommand.SMOClientCommand.ENTERROOM
    _payload = [
        (smencoder.SMPayloadType.INT, "enter", None),
        (smencoder.SMPayloadType.NT, "room", None),
        (smencoder.SMPayloadType.NT, "password", None)
    ]

class SMOPacketClientCreateRoom(SMOPacketClient):
    command = smcommand.SMOClientCommand.CREATEROOM
    _payload = [
        (smencoder.SMPayloadType.INT, "type", None),
        (smencoder.SMPayloadType.NT, "title", None),
        (smencoder.SMPayloadType.NT, "description", None),
        (smencoder.SMPayloadType.NT, "password", None)
    ]

class SMOPacketClientRoomInfo(SMOPacketClient):
    command = smcommand.SMOClientCommand.ROOMINFO
    _payload = [
        (smencoder.SMPayloadType.NT, "room", None)
    ]

class SMOPacketServerLogin(SMOPacketServer):
    command = smcommand.SMOServerCommand.LOGIN
    _payload = [
        (smencoder.SMPayloadType.INT, "approval", None),
        (smencoder.SMPayloadType.NT, "text", None)
    ]

class SMOPacketServerRoomUpdate(SMOPacketServer):
    command = smcommand.SMOServerCommand.ROOMUPDATE
    _payload = [
        (smencoder.SMPayloadType.INT, "type", None),
        (smencoder.SMPayloadType.MAP, "room_title", ("type", {
            0: (smencoder.SMPayloadType.NT, None, None),
        })),
        (smencoder.SMPayloadType.MAP, "room_description", ("type", {
            0: (smencoder.SMPayloadType.NT, None, None),
        })),
        (smencoder.SMPayloadType.MAP, "room_type", ("type", {
            0: (smencoder.SMPayloadType.INT, None, 1),
        })),
        (smencoder.SMPayloadType.MAP, "subroom", ("type", {
            0: (smencoder.SMPayloadType.INT, None, 1),
        })),
        (smencoder.SMPayloadType.MAP, "nb_rooms", ("type", {
            1: (smencoder.SMPayloadType.INT, None, 1),
        })),
        (smencoder.SMPayloadType.MAP, "rooms", ("type", {
            1: (smencoder.SMPayloadType.LIST, None, ("nb_rooms", [
                (smencoder.SMPayloadType.NT, "title", None),
                (smencoder.SMPayloadType.NT, "description", None),
            ])),
        })),
        (smencoder.SMPayloadType.MAP, "room_status", ("type", {
            1: (smencoder.SMPayloadType.INTLIST, None, (1, "nb_rooms")),
        })),
        (smencoder.SMPayloadType.MAP, "room_flags", ("type", {
            1: (smencoder.SMPayloadType.INTLIST, None, (1, "nb_rooms")),
        })),
    ]

class SMOPacketServerGeneralInfo(SMOPacketServer):
    command = smcommand.SMOServerCommand.GENERALINFO
    _payload = [
        (smencoder.SMPayloadType.INT, "format", None),
    ]

class SMOPacketServerRoomInfo(SMOPacketServer):
    command = smcommand.SMOServerCommand.ROOMINFO
    _payload = [
        (smencoder.SMPayloadType.NT, "song_title", None),
        (smencoder.SMPayloadType.NT, "song_subtitle", None),
        (smencoder.SMPayloadType.NT, "song_artist", None),
        (smencoder.SMPayloadType.INT, "num_players", None),
        (smencoder.SMPayloadType.INT, "max_players", None),
        (smencoder.SMPayloadType.NTLIST, "players", "num_players"),
    ]

class SMPacketClientNSCPing(SMPacket):
    """
        Client command 000. (Ping)

        This command will cause server to respond with a PingR Command

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketClientNSCPing()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x00'
    """

    command = smcommand.SMClientCommand.NSCPing
    _payload = []


class SMPacketClientNSCPingR(SMPacket):
    """
        Client command 001. (Ping response)

        This command is used to respond to Ping Command.

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketClientNSCPingR()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x01'
    """

    command = smcommand.SMClientCommand.NSCPingR
    _payload = []


class SMPacketClientNSCHello(SMPacket):
    """
        Client command 002. (Hello)

        This is the first packet from a client to server.

        :param int version: Client protocol version
        :param str name: Name of the stepmania build

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketClientNSCHello(
        ...     name="stepmania",
        ...     version=128
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x0c\\x02\\x80stepmania\\x00'
    """

    command = smcommand.SMClientCommand.NSCHello
    _payload = [
        (smencoder.SMPayloadType.INT, "version", None),
        (smencoder.SMPayloadType.NT, "name", None)
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
        :param str first_player_chartkey: First player's chartkey(a hash made from the notedata that's unique to each difficulty)
        :param str second_player_chartkey: Second player's chartkey
        :param str rate: An int representing the rate of the song being played( Multiplied by 100 )
        :param str filehash: the SHA1 hash of the file(Usually .sm)
    """

    command = smcommand.SMClientCommand.NSCGSR
    _payload = [
        (smencoder.SMPayloadType.MSN, "first_player_feet", None),
        (smencoder.SMPayloadType.LSN, "second_player_feet", None),
        (smencoder.SMPayloadType.MSN, "first_player_difficulty", None),
        (smencoder.SMPayloadType.LSN, "second_player_difficulty", None),
        (smencoder.SMPayloadType.MSN, "start_position", None),
        (smencoder.SMPayloadType.LSN, "reserved", None),
        (smencoder.SMPayloadType.NT, "song_title", None),
        (smencoder.SMPayloadType.NT, "song_subtitle", None),
        (smencoder.SMPayloadType.NT, "song_artist", None),
        (smencoder.SMPayloadType.NT, "course_title", None),
        (smencoder.SMPayloadType.NT, "song_options", None),
        (smencoder.SMPayloadType.NT, "first_player_options", None),
        (smencoder.SMPayloadType.NT, "second_player_options", None),
        (smencoder.SMPayloadType.NT, "first_player_chartkey", None),
        (smencoder.SMPayloadType.NT, "second_player_chartkey", None),
        (smencoder.SMPayloadType.INT, "rate", 0),
        (smencoder.SMPayloadType.NT, "filehash", None)
    ]


class SMPacketClientNSCGON(SMPacket):
    """
        Client command 004 (Game Over Notice)

        This command is sent when end of game is encounter.

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketClientNSCGON()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x04'
    """

    command = smcommand.SMClientCommand.NSCGON

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

    command = smcommand.SMClientCommand.NSCGSU
    _payload = [
        (smencoder.SMPayloadType.MSN, "player_id", None),
        (smencoder.SMPayloadType.LSN, "step_id", None),
        (smencoder.SMPayloadType.MSN, "grade", None),
        (smencoder.SMPayloadType.LSN, "note_size", None),
        (smencoder.SMPayloadType.INT, "score", 4),
        (smencoder.SMPayloadType.INT, "combo", 2),
        (smencoder.SMPayloadType.INT, "health", 2),
        (smencoder.SMPayloadType.INT, "offset", 2)
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

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketClientNSCSU(
        ...     nb_players=2,
        ...     player_id=0,
        ...     player_name="profile1",
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x0c\\x06\\x02\\x00profile1\\x00'
    """

    command = smcommand.SMClientCommand.NSCSU
    _payload = [
        (smencoder.SMPayloadType.INT, "nb_players", None),
        (smencoder.SMPayloadType.INT, "player_id", None),
        (smencoder.SMPayloadType.NT, "player_name", None),
    ]

class SMPacketClientNSCCM(SMPacket):
    """
        Client command 007 (Chat Message)

        The user typed a message for general chat.

        :param str message: The message sent by the client.

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketClientNSCCM(message="Client message")
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x10\\x07Client message\\x00'
    """

    command = smcommand.SMClientCommand.NSCCM
    _payload = [
        (smencoder.SMPayloadType.NT, "message", None),
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
        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketClientNSCRSG(
        ...     usage=2,
        ...     song_title="Title",
        ...     song_artist="Artist",
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x11\\x08\\x02Title\\x00Artist\\x00\\x00\\x00'
    """

    command = smcommand.SMClientCommand.NSCRSG
    _payload = [
        (smencoder.SMPayloadType.INT, "usage", 1),
        (smencoder.SMPayloadType.NT, "song_title", None),
        (smencoder.SMPayloadType.NT, "song_artist", None),
        (smencoder.SMPayloadType.NT, "song_subtitle", None),
        (smencoder.SMPayloadType.NT, "song_hash", None)
    ]


class SMPacketClientNSCCUUL(SMPacket):
    """
        Client command 009 (reserved)
    """

    command = smcommand.SMClientCommand.NSCCUUL

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

        >>> from smserver.smutils.smpacket import smpacket

        >>> # Client enter in room selection
        >>> packet = smpacket.SMPacketClientNSSCSMS(
        ...     action=7,
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x02\\n\\x07'
   """

    command = smcommand.SMClientCommand.NSSCSMS
    _payload = [
        (smencoder.SMPayloadType.INT, "action", None),
    ]

class SMPacketClientNSCUOpts(SMPacket):
    """
        Client command 011 (User options)

        User has changed player's options

        :param str player_0: Player 0 options
        :param str player_1: Player 1 options
    """

    command = smcommand.SMClientCommand.NSCUOpts
    _payload = [
        (smencoder.SMPayloadType.NT, "player_0", None),
        (smencoder.SMPayloadType.NT, "player_1", None),
    ]


class SMPacketClientNSSMONL(SMPacket):
    """
        Client command 012 (SMOnline Packet)

        The SMLan packet 12 is a wrapper for the SMOnline packet.

        :param packet: The SMOPacket to include
        :type packet: SMOPacketClient
    """

    command = smcommand.SMClientCommand.NSSMONL
    _payload = [
        (smencoder.SMPayloadType.PACKET, "packet", SMOPacketClient)
    ]

class SMPacketClientNSCFormatted(SMPacket):
    """
        Client command 013 (reserved)
    """

    command = smcommand.SMClientCommand.NSCFormatted

class SMPacketClientNSCAttack(SMPacket):
    """
        Client command 014 (reserved)
    """

    command = smcommand.SMClientCommand.NSCAttack

class SMPacketClientXMLPacket(SMPacket):
    """
        Client command 15 (XMLPacket)

        This packet contains data in XML format.

        :param str xml: XML string
    """

    command = smcommand.SMClientCommand.XMLPacket
    _payload = [
        (smencoder.SMPayloadType.NT, "xml", None),
    ]

class SMPacketClientFLU(SMPacket):
    """
        Client command 16 (FLU)
        RESERVED
    """

    command = smcommand.SMClientCommand.FLU
    _payload = [
    ]

class SMPacketServerNSCPing(SMPacket):
    """
        Server command 128 (Ping)

        This command will cause client to respond with a PingR command

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketServerNSCPing()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x80'
    """

    command = smcommand.SMServerCommand.NSCPing

class SMPacketServerNSCPingR(SMPacket):
    """
        Server command 129 (PingR)

        This command is used to respond to a Ping command.

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketServerNSCPingR()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x81'
    """

    command = smcommand.SMServerCommand.NSCPingR

class SMPacketServerNSCHello(SMPacket):
    """
        Server command 130 (Hello)

        This command introduces the server. (In response of Client Hello
        command)

        :param str version: The server protocol version (always 128)
        :param str name: Name of the server
        :param int key: Random key, used for hash password

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketServerNSCHello(
        ...     version=128,
        ...     name="MyServer",
        ...     key=999999999
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x0f\\x82\\x80MyServer\\x00;\\x9a\\xc9\\xff'
    """

    command = smcommand.SMServerCommand.NSCHello
    _payload = [
        (smencoder.SMPayloadType.INT, "version", None),
        (smencoder.SMPayloadType.NT, "name", None),
        (smencoder.SMPayloadType.INT, "key", 4)
    ]

class SMPacketServerNSCGSR(SMPacket):
    """
        Server command 131 (Allow Start)

        This will cause the client to start the game

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketServerNSCGSR()
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x01\\x83'
    """

    command = smcommand.SMServerCommand.NSCGSR

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

    command = smcommand.SMServerCommand.NSCGON
    _payload = [
        (smencoder.SMPayloadType.INT, "nb_players", 1),
        (smencoder.SMPayloadType.INTLIST, "ids", (1, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "score", (4, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "grade", (1, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "difficulty", (1, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "flawless", (2, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "perfect", (2, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "great", (2, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "good", (2, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "bad", (2, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "miss", (2, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "held", (2, "nb_players")),
        (smencoder.SMPayloadType.INTLIST, "max_combo", (2, "nb_players")),
        (smencoder.SMPayloadType.NTLIST, "options", "nb_players"),
    ]

class SMPacketServerNSCGSU(SMPacket):
    """
        Server command 133 (Scoreboard update)

        This will update the client's scoreboard.

        :param int section: Which section to update (0: names, 1:combos, 2: grades)
        :param int nb_players: Nb of plyaers in this packet
        :param list options: Int list contining names, combos or grades

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketServerNSCGSU(
        ...     section=1, # Update the actual combo
        ...     nb_players=2, # 2 users in this packet
        ...     options=[12, 5] # List containing the combos
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x07\\x85\\x01\\x02\\x00\\x0c\\x00\\x05'
    """

    command = smcommand.SMServerCommand.NSCGSU
    _payload = [
        (smencoder.SMPayloadType.INT, "section", 1),
        (smencoder.SMPayloadType.INT, "nb_players", 1),
        (smencoder.SMPayloadType.MAP, "options", ("section", {
            0: (smencoder.SMPayloadType.INTLIST, None, (1, "nb_players")),
            1: (smencoder.SMPayloadType.INTLIST, None, (2, "nb_players")),
            2: (smencoder.SMPayloadType.INTLIST, None, (1, "nb_players")),
        }))
    ]

class SMPacketServerNSCSU(SMPacket):
    """
        Server command 134 (System Message)

        Send a system message to user

        :param str message: The message to send

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketServerNSCSU(message="System message")
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x10\\x86System message\\x00'
    """

    command = smcommand.SMServerCommand.NSCSU
    _payload = [
        (smencoder.SMPayloadType.NT, "message", None)
    ]

class SMPacketServerNSCCM(SMPacket):
    """
        Server command 135 (Chat Message)

        Add a chat message to the chat window on some StepMania screens.

        :param str message: The message to add

        :Example:

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketServerNSCSU(message="Client message")
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x10\\x86Client message\\x00'
    """

    command = smcommand.SMServerCommand.NSCCM
    _payload = [
        (smencoder.SMPayloadType.NT, "message", None)
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

        >>> from smserver.smutils.smpacket import smpacket
        >>> packet = smpacket.SMPacketServerNSCRSG(
        ...     usage=0, # Check song presence
        ...     song_title="title",
        ...     song_artist="artist",
        ...     song_subtitle="subtitle",
        ... )
        >>> print(packet.binary)
        b'\\x00\\x00\\x00\\x19\\x88\\x00title\\x00artist\\x00subtitle\\x00\\x00'
    """

    command = smcommand.SMServerCommand.NSCRSG
    _payload = [
        (smencoder.SMPayloadType.INT, "usage", 1),
        (smencoder.SMPayloadType.NT, "song_title", None),
        (smencoder.SMPayloadType.NT, "song_artist", None),
        (smencoder.SMPayloadType.NT, "song_subtitle", None),
        (smencoder.SMPayloadType.NT, "song_hash", None)
    ]


class SMPacketServerNSCCUUL(SMPacket):
    """
        Server command 137 (Update user list)

        This sends all the users currently connected

        :param int max_players: NB max of players (max 255)
        :param int nb_players: NB of player's in this packet
        :param list players: List containing status and name for each user
    """

    command = smcommand.SMServerCommand.NSCCUUL
    _payload = [
        (smencoder.SMPayloadType.INT, "max_players", 1),
        (smencoder.SMPayloadType.INT, "nb_players", 1),
        (smencoder.SMPayloadType.LIST, "players", ("nb_players", [
            (smencoder.SMPayloadType.INT, "status", 1),
            (smencoder.SMPayloadType.NT, "name", None),
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

    command = smcommand.SMServerCommand.NSSCSMS
    _payload = [
        (smencoder.SMPayloadType.NT, "gametype", None),
        (smencoder.SMPayloadType.NT, "style", None),
    ]


class SMPacketServerNSCUOpts(SMPacket):
    """
        Server command 139 (reserved)
    """

    command = smcommand.SMServerCommand.NSCUOpts

class SMPacketServerNSSMONL(SMPacket):
    """
        Server command 140 (SMOnline Packet)

        The SMLan packet 140 is a wrapper for the SMOnline packet.

        :param packet: The SMOPacket to include
        :type packet: SMOPacketServer
    """

    command = smcommand.SMServerCommand.NSSMONL
    _payload = [
        (smencoder.SMPayloadType.PACKET, "packet", SMOPacketServer)
    ]

class SMPacketServerNSCFormatted(SMPacket):
    """
        Server command 141 (Formatted information packet)

        Send formatted information regarding the server back to the player.

        :param str server_name: Server name
        :param int server_port: Port the server is listening on
        :param int nb_players: Number of players connected
    """

    command = smcommand.SMServerCommand.NSCFormatted
    _payload = [
        (smencoder.SMPayloadType.NT, "server_name", None),
        (smencoder.SMPayloadType.INT, "server_port", 2),
        (smencoder.SMPayloadType.INT, "nb_players", 2),
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

        >>> from smserver.smutils.smpacket import smpacket
        >>> from smserver.smutils import smattack
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

    command = smcommand.SMServerCommand.NSCAttack
    _payload = [
        (smencoder.SMPayloadType.INT, "player", 1),
        (smencoder.SMPayloadType.INT, "time", 4),
        (smencoder.SMPayloadType.NT, "attack", None),
    ]


class SMPacketServerXMLPacket(SMPacket):
    """
        Server command 143 (XMLPacket)

        This packet contains data in XML format.

        :param str xml: XML string
    """

    command = smcommand.SMServerCommand.XMLPacket
    _payload = [
        (smencoder.SMPayloadType.NT, "xml", None),
    ]

class SMPacketServerFLU(SMPacket):
    """
        Server command 144 (FLU)
        This packet contains friendlist data.
        :param str usernames : usernames
        :param str userstates : usertates
    """

    command = smcommand.SMServerCommand.FLU
    _payload = [
        (smencoder.SMPayloadType.INT, "nb_players", 1),
        (smencoder.SMPayloadType.LIST, "players", ("nb_players", [
            (smencoder.SMPayloadType.INT, "status", 1),
            (smencoder.SMPayloadType.NT, "name", None),
            ])
        )
    ]
