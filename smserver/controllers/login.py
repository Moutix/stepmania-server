#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models
from smserver import __version__

class LoginController(StepmaniaController):
    command = smpacket.SMOClientCommand.LOGIN
    require_login = False

    def handle(self):
        connected = self.server.auth.login(self.packet["username"], self.packet["password"])

        if not connected:
            self.log.info("Player %s failed to connect" % self.packet["username"])
            self.send(smpacket.SMPacketServerNSSMONL(
                packet=smpacket.SMOPacketServerLogin(
                    approval=1,
                    text="Connection failed for user %s" % self.packet["username"]
                )
            ))
            return

        nb_onlines = models.User.nb_onlines(self.session)
        max_users = self.server.config.server.get("max_users", -1)
        if max_users > 0 and nb_onlines >= max_users:
            self.log.info("Player %s cannot login, nb max of user reaches", self.packet["username"])
            self.send(smpacket.SMPacketServerNSSMONL(
                packet=smpacket.SMOPacketServerLogin(
                    approval=1,
                    text="Can't login, nb max users reaches (%s/%s)" % (nb_onlines, max_users)
                )
            ))
            return

        try:
            user = models.User.connect(self.packet["username"], self.packet["player_number"], self.session)
        except models.user.AlreadyConnectError as err:
            if err.user.id in self.conn.users:
                user = err.user
                user.pos = self.packet["player_number"]
            else:
                self.log.info("Player %s is already connected", self.packet["username"])
                self.send(smpacket.SMPacketServerNSSMONL(
                    packet=smpacket.SMOPacketServerLogin(
                        approval=1,
                        text="User %s is already connected" % self.packet["username"]
                    )
                ))
                return

        if models.Ban.is_ban(self.session, user_id=user.id):
            self.log.info("Connection failed for ban user %s", self.packet["username"])
            self.send(smpacket.SMPacketServerNSSMONL(
                packet=smpacket.SMOPacketServerLogin(
                    approval=1,
                    text="User %s is ban from this server" % self.packet["username"]
                )
            ))
            return

        self.log.info("Player %s successfully connect" % self.packet["username"])

        user.last_ip = self.conn.ip
        user.stepmania_name = self.conn.stepmania_name
        user.stepmania_version = self.conn.stepmania_version

        self.session.commit()

        self.conn.chat_timestamp = user.chat_timestamp

        for online_user in self.users:
            if online_user.pos == self.packet["player_number"] and online_user.name != user.name:
                online_user.pos = None
                online_user.online = False

        if not self.conn.users:
            self._send_server_resume(nb_onlines, max_users)

        if user.id not in self.conn.users:
            self.conn.users.append(user.id)

        self.session.commit()

        self.server.enter_room(self.room, conn=self.conn)

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=smpacket.SMOPacketServerLogin(
                approval=0,
                text="Player %s successfully login" % self.packet["username"]
            )
        ))



        self.send(models.Room.smo_list(self.session, self.active_users))
        self.server.send_sd_running_status()
        friends = self.session.query(models.Friendship).filter_by(state = 1).filter((models.Friendship.user1_id == user.id) | (models.Friendship.user2_id == user.id)).all()
        for friend in friends:
            if friend.user1_id == user.id:
                friendid = friend.user2_id
            else:
                friendid = friend.user1_id
            friendconn = self.server.find_connection(friendid)
            self.server.send_friend_list(friendid, friendconn)
            frienduser = self.session.query(models.User).filter_by(id = friendid).first()
            if frienduser.online == True and frienduser.friend_notifications == True and friendconn:
                self.send_message(
                    "Your friend %s connected" % user.name,
                    friendconn
                )

        self.server.send_friend_list(user.id, self.conn)
        
    def _send_server_resume(self, nb_onlines, max_users):
        self.send_message(self.server.config.server.get("motd", ""), to="me")
        self.send_message(
            "SMServer v%s, started on %s. %s/%s users online" % (
                __version__,
                self.server.started_at.strftime("%x at %X"),
                nb_onlines + 1,
                max_users if max_users > 0 else "--"
                ),
            to="me")

