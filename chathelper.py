#!/usr/bin/env python3
# -*- coding: utf8 -*-

from colorsys import hls_to_rgb

def chat_color(color):
    return "|c0%s" % color

def with_color(message, color=None):
    if not color:
        color = nick_color(message)

    return "%s%s%s" % (chat_color(color), message, chat_color("ffffff"))

def nick_color(nick):
    nick_int = sum(ord(n) for n in nick)

    color = hls_to_rgb(nick_int % 100 / 100, 0.5, 0.5)

    return ''.join(["{0:x}".format(int(c*256)) for c in color])

if __name__ == "__main__":
    print(nick_color("ningirsu"))
    print(nick_color("taemin"))
    print(with_color("ningirsu"))
