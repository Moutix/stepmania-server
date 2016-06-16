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
    return "|c0%s" % color

def with_color(message, color=None):
    if not color:
        color = nick_color(message)

    return "%s%s%s" % (chat_color(color), message, chat_color("ffffff"))

def nick_color(nick):
    try:
        return STATIC_COLOR[nick.lower()]
    except KeyError:
        pass

    nick_int = sum(ord(n)*3 for n in nick)

    hue = (nick_int % 100) / 100

    color = hls_to_rgb(hue, 0.5, 0.9)

    return ''.join(["{:02x}".format(int(c*255)) for c in color])

if __name__ == "__main__":
    print(nick_color("ningirsu"))
    print(nick_color("taemin"))
    print(nick_color("jungkook"))
    print(nick_color("paf"))
