#!/usr/bin/env python3
# -*- coding: utf8 -*-

from colorsys import hls_to_rgb

STATIC_COLOR = {
    "aaaa": "a78a01",
    "aaa": "4a8601",
    "aa": "01688f",
    "a": "005ad0",
    "b": "017f25",
    "c": "016d63",
    "d": "e9014d",
    "f": "eb2701",
    "beginner": "86355a",
    "easy": "347300",
    "medium": "847402",
    "hard": "833310",
    "expert": "31725e",
}

def chat_color(color):
    """
        Stepmania chat color format

        :param str color: Color in hex format

        :Example:

        >>> chat_color("cecece")
        '|c0cecece'
    """


    return "|c0%s" % color

def with_color(message, color=None):
    """
        Add a color to a message, for Stepmania Chat.

        If no color is provided, it guess the color with `nick_color`

        :param str message: Message to color
        :param str color: Color in hex format

        :Example:

        >>> with_color("Hello")
        '|c0f20c0cHello|c0ffffff'

        >>> with_color("Hello", "cecece")
        '|c0cececeHello|c0ffffff'
    """

    if not color:
        color = nick_color(message)

    return "%s%s%s" % (chat_color(color), message, chat_color("ffffff"))

def nick_color(nick):
    """
        Generate a color from a given string.

        :param str nick: Input string
        :return: A hex color
        :rtype: str

        >>> nick_color("A")
        '005ad0'

        >>> nick_color("Hello!")
        'f20c1a'
    """
    try:
        return STATIC_COLOR[nick.lower()]
    except KeyError:
        pass

    nick_int = sum(ord(n)*3 for n in nick)

    hue = (nick_int % 100) / 100

    color = hls_to_rgb(hue, 0.5, 0.9)

    return ''.join(["{:02x}".format(int(c*255)) for c in color])

if __name__ == "__main__":
    import doctest
    doctest.testmod()
