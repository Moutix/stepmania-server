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
    nick_int = sum(ord(n)*3 for n in nick)

    hue = (nick_int % 100) / 100

    color = hls_to_rgb(hue, 0.5, 0.9)

    return ''.join(["{:02x}".format(int(c*255)) for c in color])

if __name__ == "__main__":
    print(nick_color("ningirsu"))
    print(nick_color("taemin"))
    print(nick_color("jungkook"))
    print(nick_color("paf"))
