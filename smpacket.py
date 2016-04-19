from enum import Enum

class ParentCommand(Enum):
    @classmethod
    def get(cls, value, default=None):
        for klass in cls.__subclasses__():
            try:
                return klass(value)
            except ValueError:
                pass

        return default

class SMCommand(ParentCommand):
    pass

class SMClientCommand(SMCommand):
    NSCPing = 0
    NSCPingR = 1
    NSCHello = 2
    NSCGSR = 3
    NSCGON = 4
    NSCGSU = 5
    NSCSU = 6
    NSCCM = 7
    NSCRSG = 8
    NSCCUUL = 9
    NSSCSMS = 10
    NSCUOpts = 11
    NSSMONL = 12
    NSCFormatted = 13
    NSCAttack = 14
    XMLPacket = 15

class SMServerCommand(SMCommand):
    NSCPing = 128
    NSCPingR = 129
    NSCHello = 130
    NSCGSR = 131
    NSCGON = 132
    NSCGSU = 133
    NSCSU = 144
    NSCCM = 145
    NSCRSG = 146
    NSCCUUL = 147
    NSSCSMS = 148
    NSCUOpts = 149
    NSSMONL = 150
    NSCFormatted = 151
    NSCAttack = 152
    XMLPacket = 153

class SMOCommand(ParentCommand):
    pass

class SMOClientCommand(Enum):
    LOGIN = 0
    ENTERROOM = 1
    CREATEROOM = 2
    ROOMINFO = 3

class SMOServerCommand(Enum):
    LOGIN = 0
    ROOMUPDATE = 1
    GENERALINFO = 3
    ROOMINFO = 4

class SMPayloadTypeAbstract(object):
    @staticmethod
    def encode(data):
        return b''

    @staticmethod
    def decode(payload):
        return payload, None

class SMPayloadTypeNT(SMPayloadTypeAbstract):
    @staticmethod
    def encode(data):
        if not data:
            return b'\x00'
        return data.replace('\x00', '').encode('utf-8') + b'\x00'

    @staticmethod
    def decode(payload):
        tmp = payload.split(b'\x00', 1)
        if len(tmp) < 2:
            return payload, None
        return tmp[1], tmp[0].decode('utf-8')

class SMPayloadTypeNTList(SMPayloadTypeAbstract):
    @staticmethod
    def encode(data):
        if not data:
            return b'\x00'
        return b'\x00'.join([d.replace('\x00', '').encode('utf-8') for d in data]) + b'\x00'

    @staticmethod
    def decode(payload):
        tmp = [p.decode('utf-8') for p in payload.split(b'\x00')]
        if not tmp:
            return payload, None

        return '\x00', tmp[:-1]


class SMPayloadTypeSMOClient(SMPayloadTypeAbstract):
    @staticmethod
    def encode(data):
        if not data:
            return b''
        return data.data

    @staticmethod
    def decode(payload):
        tmp = SMOPacketClient.parse_binary(payload)
        if not tmp:
            return payload, None
        return payload[len(tmp.payload):], tmp

class SMPayloadTypeSMOServer(SMPayloadTypeAbstract):
    @staticmethod
    def encode(data):
        if not data:
            return b''
        return data.data

    @staticmethod
    def decode(payload):
        tmp = SMOPacketServer.parse_binary(payload)
        if not tmp:
            return payload, None
        return payload[len(tmp.payload):], tmp


class SMPayloadType(Enum):
    MSN = 1
    LSN = 2
    NT = SMPayloadTypeNT
    NTList = SMPayloadTypeNTList
    SMOClient = SMPayloadTypeSMOClient
    SMOServer = SMPayloadTypeSMOServer

class SMPacket(object):
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
        payload = b""
        byte = ""

        for size, name in self._payload:
            if isinstance(size, int):
                payload += self.opts.get(name, 0).to_bytes(size, byteorder='big')
                continue

            if size == SMPayloadType.MSN:
                byte += self._to_bin_str(self.opts.get(name, 0))
                continue

            if size == SMPayloadType.LSN:
                byte += self._to_bin_str(self.opts.get(name, 0))
                payload += bytes([int(byte, 2)])
                byte = ""
                continue

            res = size.value.encode(self.opts.get(name))
            if not res:
                continue
            payload += res

        return payload

    @classmethod
    def from_payload(cls, payload):
        opts = {}
        for size, name in cls._payload:
            if isinstance(size, int):
                opts[name] = int.from_bytes(payload[:size], byteorder='big')
                payload = payload[size:]
                continue

            if size == SMPayloadType.MSN:
                opts[name] = int(cls._to_bin_str(payload[0], 8)[:4], 2)
                continue

            if size == SMPayloadType.LSN:
                opts[name] = int(cls._to_bin_str(payload[0], 8)[4:], 2)
                payload = payload[1:]
                continue

            payload, opts[name] = size.value.decode(payload)

        return cls(**opts)

    @classmethod
    def parse_binary(cls, binary):
        if len(binary) < 4:
            return None

        binary = binary[4:]

        command = SMCommand.get(binary[0])
        if not command:
            return None

        return cls.get_class(command).from_payload(binary[1:])

    @staticmethod
    def _to_bin_str(number, size=4):
        number = "{0:b}".format(number)
        if len(number) == size:
            return number

        if len(number) > size:
            return "1"*size

        return "0"*(size-len(number)) + number

class SMPacketClientNSCPing(SMPacket):
    _command = SMClientCommand.NSCPing
    _payload = []


class SMPacketClientNSCPingR(SMPacket):
    _command = SMClientCommand.NSCPingR
    _payload = []


class SMPacketClientNSCHello(SMPacket):
    _command = SMClientCommand.NSCHello
    _payload = [
        (1, "version"),
        (SMPayloadType.NT, "name")
    ]

class SMPacketClientNSCGSR(SMPacket):
    _command = SMClientCommand.NSCGSR
    _payload = [
        (SMPayloadType.MSN, "first_player_feet"),
        (SMPayloadType.LSN, "second_player_feet"),
        (SMPayloadType.MSN, "first_player_difficulty"),
        (SMPayloadType.LSN, "second_player_difficulty"),
        (SMPayloadType.MSN, "start_position"),
        (SMPayloadType.LSN, "reserved"),
        (SMPayloadType.NT, "song_title"),
        (SMPayloadType.NT, "song_subtitle"),
        (SMPayloadType.NT, "song_artist"),
        (SMPayloadType.NT, "course_title"),
        (SMPayloadType.NT, "song_options"),
        (SMPayloadType.NT, "first_player_options"),
        (SMPayloadType.NT, "second_player_options"),
    ]


class SMPacketClientNSCGON(SMPacket):
    _command = SMClientCommand.NSCGON

class SMPacketClientNSCGSU(SMPacket):
    _command = SMClientCommand.NSCGSU
    _payload = [
        (SMPayloadType.MSN, "player_id"),
        (SMPayloadType.LSN, "step_id"),
        (SMPayloadType.MSN, "grade"),
        (SMPayloadType.LSN, "reserved"),
        (4, "score"),
        (2, "combo"),
        (2, "health"),
        (2, "offset")
    ]

class SMPacketClientNSCSU(SMPacket):
    _command = SMClientCommand.NSCSU

class SMPacketClientNSCCM(SMPacket):
    _command = SMClientCommand.NSCCM

class SMPacketClientNSCRSG(SMPacket):
    _command = SMClientCommand.NSCRSG

class SMPacketClientNSCCUUL(SMPacket):
    _command = SMClientCommand.NSCCUUL

class SMPacketClientNSSCSMS(SMPacket):
    _command = SMClientCommand.NSSCSMS

class SMPacketClientNSCUOpts(SMPacket):
    _command = SMClientCommand.NSCUOpts

class SMPacketClientNSSMONL(SMPacket):
    _command = SMClientCommand.NSSMONL
    _payload = [
        (SMPayloadType.SMOClient, "packet")
    ]

class SMPacketClientNSCFormatted(SMPacket):
    _command = SMClientCommand.NSCFormatted

class SMPacketClientNSCAttack(SMPacket):
    _command = SMClientCommand.NSCAttack

class SMPacketClientXMLPacket(SMPacket):
    _command = SMClientCommand.XMLPacket

class SMPacketServerNSCPing(SMPacket):
    _command = SMServerCommand.NSCPing

class SMPacketServerNSCPingR(SMPacket):
    _command = SMServerCommand.NSCPingR

class SMPacketServerNSCHello(SMPacket):
    _command = SMServerCommand.NSCHello
    _payload = [
        (1, "version"),
        (SMPayloadType.NT, "name"),
        (4, "key")
    ]

class SMPacketServerNSCGSR(SMPacket):
    _command = SMServerCommand.NSCGSR

class SMPacketServerNSCGON(SMPacket):
    _command = SMServerCommand.NSCGON

class SMPacketServerNSCGSU(SMPacket):
    _command = SMServerCommand.NSCGSU

class SMPacketServerNSCSU(SMPacket):
    _command = SMServerCommand.NSCSU

class SMPacketServerNSCCM(SMPacket):
    _command = SMServerCommand.NSCCM

class SMPacketServerNSCRSG(SMPacket):
    _command = SMServerCommand.NSCRSG

class SMPacketServerNSCCUUL(SMPacket):
    _command = SMServerCommand.NSCCUUL

class SMPacketServerNSSCSMS(SMPacket):
    _command = SMServerCommand.NSSCSMS

class SMPacketServerNSCUOpts(SMPacket):
    _command = SMServerCommand.NSCUOpts

class SMPacketServerNSSMONL(SMPacket):
    _command = SMServerCommand.NSSMONL
    _payload = [
        (SMPayloadType.SMOServer, "packet")
    ]

class SMPacketServerNSCFormatted(SMPacket):
    _command = SMServerCommand.NSCFormatted

class SMPacketServerNSCAttack(SMPacket):
    _command = SMServerCommand.NSCAttack

class SMPacketServerXMLPacket(SMPacket):
    _command = SMServerCommand.XMLPacket

class SMOPacketClient(SMPacket):
    @classmethod
    def parse_binary(cls, binary):
        try:
            command = SMOClientCommand(binary[0])
        except KeyError:
            return None

        return cls.get_class(command).from_payload(binary[1:])

class SMOPacketClientLogin(SMOPacketClient):
    _command = SMOClientCommand.LOGIN
    _payload = [
        (1, "player_number"),
        (1, "encryption"),
        (SMPayloadType.NT, "username"),
        (SMPayloadType.NT, "password")
    ]

class SMOPacketClientEnterRoom(SMOPacketClient):
    _command = SMOClientCommand.ENTERROOM
    _payload = [
        (1, "enter"),
        (SMPayloadType.NT, "room"),
        (SMPayloadType.NT, "password")
    ]

class SMOPacketClientCreateRoom(SMOPacketClient):
    _command = SMOClientCommand.CREATEROOM
    _payload = [
        (1, "type"),
        (SMPayloadType.NT, "title"),
        (SMPayloadType.NT, "description"),
        (SMPayloadType.NT, "password")
    ]

class SMOPacketClientRoomInfo(SMOPacketClient):
    _command = SMOClientCommand.ROOMINFO
    _payload = [
        (SMPayloadType.NT, "room")
    ]

class SMOPacketServer(SMPacket):
    @classmethod
    def parse_binary(cls, binary):
        try:
            command = SMOServerCommand(binary[0])
        except KeyError:
            return None

        return cls.get_class(command).from_payload(binary[1:])

class SMOPacketServerLogin(SMOPacketServer):
    _command = SMOServerCommand.LOGIN
    _payload = [
        (1, "approval"),
        (SMPayloadType.NT, "text")
    ]

class SMOPacketServerRoomUpdate(SMOPacketServer):
    _command = SMOServerCommand.ROOMUPDATE
    _payload = [
        (1, "type"),
    ]

class SMOPacketServerGeneralInfo(SMOPacketServer):
    _command = SMOServerCommand.GENERALINFO
    _payload = [
        (1, "format"),
    ]

class SMOPacketServerRoomInfo(SMOPacketServer):
    _command = SMOServerCommand.ROOMINFO
    _payload = [
        (SMPayloadType.NT, "song_title"),
        (SMPayloadType.NT, "song_subtitle"),
        (SMPayloadType.NT, "song_artist"),
        (1, "num_players"),
        (1, "max_players"),
        (SMPayloadType.NTList, "players"),
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
    assert packet.binary == SMPacket.parse_binary(packet.binary).binary

    packet = SMPacket.new(
        SMServerCommand.NSSMONL,
        packet=SMOPacketServer.new(
            SMOServerCommand.ROOMINFO,
            song_title="song_title",
            players=["bidule", "machin", "trux"]
        )
    )

    print(packet)
    assert packet.binary == SMPacket.parse_binary(packet.binary).binary

if __name__ == "__main__":
    main()
