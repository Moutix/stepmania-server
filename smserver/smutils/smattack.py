#!/usr/bin/env python3
# -*- coding: utf8 -*-

""" Import the list of available attacks in stepmania """

from enum import Enum

class SMAttack(Enum):
    """ Represent all the attacks available """

    Clearall       = 'clearall'
    Boost          = 'boost'
    Brake          = 'brake'
    Wave           = 'wave'
    Boomerang      = 'boomerang'
    Drunk          = 'drunk'
    Dizzy          = 'dizzy'
    Confusion      = 'confusion'
    Mini           = 'mini'
    Tiny           = 'tiny'
    Flip           = 'flip'
    Invert         = 'invert'
    Tornado        = 'tornado'
    Tipsy          = 'tipsy'
    Bumpy          = 'bumpy'
    Beat           = 'beat'
    Xmode          = 'xmode'
    Twirl          = 'twirl'
    Roll           = 'roll'
    Hidden         = 'hidden'
    Hiddenoffset   = 'hiddenoffset'
    Sudden         = 'sudden'
    Suddenoffset   = 'suddenoffset'
    Stealth        = 'stealth'
    Blink          = 'blink'
    Randomvanish   = 'randomvanish'
    Reverse        = 'reverse'
    Split          = 'split'
    Alternate      = 'alternate'
    Cross          = 'cross'
    Centered       = 'centered'
    Dark           = 'dark'
    Blind          = 'blind'
    Cover          = 'cover'
    Randomattacks  = 'randomattacks'
    Noattacks      = 'noattacks'
    Playerautoplay = 'playerautoplay'
    Passmark       = 'passmark'
    Randomspeed    = 'randomspeed'
    Converge       = 'converge'
