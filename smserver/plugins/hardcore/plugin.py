#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
    The hardcore plugin add a hardcore mode in the room.

    You can enable it by typing /hardcore.
"""


import random

from smserver import pluginmanager, chatplugin, stepmania_controller, models, ability
from smserver.smutils import smpacket, smattack

class HardcoreChatPlugin(chatplugin.ChatPlugin):
    """
        Add the hadcore command in the chat.

        /hardcore will enable or disable the hardcore mode for the current room
    """


    command = "hardcore"
    helper = "Change toom mode to hardcore"
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, serv, message):
        if serv.room.mode == "hardcore":
            serv.room.mode = None
            msg = "The room is now in normal mode"
        else:
            serv.room.mode = "hardcore"
            msg = "The room is now in hardcore mode"

        serv.session.commit()
        serv.send_message(msg)


class HardcorePlugin(pluginmanager.StepmaniaPlugin):
    """
        Plugin to handle each new GSU packet.

        Send an attack to everybody each time a player accumulate enought point
    """


    def __init__(self, server):
        pluginmanager.StepmaniaPlugin.__init__(self, server)

        self.config = server.config.plugins["hardcore"]
        if not self.config:
            self.config = {}

        self.conf_weight = server.config.score.get("percentWeight")
        if not self.conf_weight:
            self.conf_weight = {
                "not_held": 0,
                "miss": 0,
                "bad": 0,
                "good": 0,
                "held": 3,
                "hit_mine": -2,
                "great": 1,
                "perfect": 2,
                "flawless": 3
            }

    def on_nscgsu(self, session, serv, packet):
        """
            This method is called on each nscgsu packet.
        """

        if not serv.room:
            return

        player_id = packet["player_id"]

        if player_id not in (0, 1):
            return

        if "attack_metter" not in serv.songstats[player_id]:
            return

        self.update_score(serv, player_id, packet["step_id"])

        if serv.songstats[player_id]["attack_metter"] > self.config.get("max_metter", 100):
            self.send_attack(serv, player_id, session)

    def update_score(self, serv, player_id, stepid):
        """
            Update the score of the given player
        """

        step = models.SongStat.stepid.get(stepid)
        if not step:
            return

        with serv.mutex:
            serv.songstats[player_id]["attack_metter"] += self.conf_weight.get(step, 0)

        print(serv.songstats[player_id]["attack_metter"])

    def send_attack(self, serv, player_id, session):
        """
            Send an attack to every players except the current one
        """

        with serv.mutex:
            serv.songstats[player_id]["attack_metter"] = 0

        attack = random.choice(list(smattack.SMAttack))

        packet = smpacket.SMPacketServerNSCAttack(
            time=self.config.get("attack_duration", 3000),
            attack=attack
        )

        user = models.User.get_from_pos(serv.users, player_id, session)

        message = smpacket.SMPacketServerNSCSU(
            message="%s send an attack: %s" % (user.fullname(serv.room), attack.value)
        )

        for conn in self.server.ingame_connections(serv.room):
            for player in (0, 1):
                if conn == serv and player_id == player:
                    continue

                packet["player"] = player
                conn.send(packet)

            conn.send(message)


class HardcoreStartControllerPlugin(stepmania_controller.StepmaniaController):
    command = smpacket.SMClientCommand.NSCGSR
    require_login = True

    def handle(self):
        """
            Activate the hardocre mode if the room status is in hardocre when
            a game start
        """

        if not self.room:
            return

        if self.room.status != 2 or self.room.mode != "hardcore":
            return

        with self.conn.mutex:
            self.conn.songstats[0]["attack_metter"] = 0
            self.conn.songstats[1]["attack_metter"] = 0

