""" Stepmania packet encoder module

Provide method to encode dict in correct stepmania payload
"""

import abc
import json

from enum import Enum

class SMPayloadTypeAbstract(metaclass=abc.ABCMeta):
    """
        Parent class for declaring new type of data.
    """

    DEFAULT = None

    @staticmethod
    @abc.abstractmethod
    def encode(_data, _opt=None):
        """
            Define here how the data is encoded.

            Take the data and option and return the encoded data
        """

        return b''

    @staticmethod
    @abc.abstractmethod
    def decode(payload, _opt=None):
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
    def encode(data, _opt=None):
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
    def decode(payload, _opt=None):
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

        return b''.join(BinaryEncoder.encode(d, opt[1]) for d in data)

    @staticmethod
    def decode(payload, opt=None):
        if not opt:
            opt = [1, []]

        res = []
        for _ in range(0, opt[0]):
            payload, tmp = BinaryEncoder.decode(payload, opt[1])
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
    def encode(data, _opt=None):
        if not data:
            return b''

        return data.data

    @staticmethod
    def decode(payload, opt=None):
        if not opt:
            return payload, None

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

class Encoder(metaclass=abc.ABCMeta):
    """ Base class for encoder module """

    @staticmethod
    @abc.abstractmethod
    def encode(values, payload_option, command=None):
        """ Encode the given values according to the payload_option

        :param dict values: Params to encode
        :param list payload_option: List of options which indicate how
        to encode each field
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def decode(payload, payload_option):
        """ Decode the given payload according to the payload option

        :param str payload: Payload to decode
        :param list payload_option: List of options which indicate how
        to encode each field
        """
        pass

class BinaryEncoder(Encoder):
    """ Binary encoder to encding in the stepmania legacy protocol """

    @classmethod
    def encode(cls, values, payload_option, _command=None):
        """ Encode data in binary format """

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

            res = size.value.encode(
                values.get(name),
                cls._replace_from_options(values, opt)
            )

            if not res:
                continue

            payload += res

        return payload

    @classmethod
    def decode(cls, payload, payload_option):
        """ Decode data in binary format """

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


class JSONEncoder(Encoder):
    """ JSON encoder to encode data in the stepmania protocol """


    @classmethod
    def encode(cls, values, payload_option, command=None):
        """ Encode values in a correct json payload """

        data = {}

        if command is not None:
            data["_command"] = command

        for size, name, _opt in payload_option:
            if size == SMPayloadType.PACKET and name in values:
                data[name] = values[name].json
                continue

            if isinstance(size.value, int):
                default = 0
            else:
                default = size.value.DEFAULT

            data[name] = values.get(name, default)

        return json.dumps(data)

    @classmethod
    def decode(cls, payload, payload_option):
        """ Decode a payload in a valid dict given the payload option """

        opts = json.loads(payload)

        data = {}

        for size, name, opt in payload_option:
            if size == SMPayloadType.PACKET and opts.get(name):
                data[name] = opt.parse_json(opts[name])
                continue

            if isinstance(size.value, int):
                default = 0
            else:
                default = size.value.DEFAULT

            data[name] = opts.get(name, default)

        return data
