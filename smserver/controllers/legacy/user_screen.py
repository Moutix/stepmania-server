""" User status controller """

from smserver.smutils.smpacket import smcommand
from smserver.stepmania_controller import StepmaniaController
from smserver import models

class UserStatusController(StepmaniaController):
    command = smcommand.SMClientCommand.NSSCSMS
    require_login = True

    def handle(self):
        status_mapping = {
            1: models.UserStatus.music_selection,
            3: models.UserStatus.option,
            5: models.UserStatus.evaluation,
            7: models.UserStatus.room_selection
        }

        if self.packet["action"] == 7:
            self.conn.room = None
            for user in self.active_users:
                user.room = None
            for room in self.session.query(models.Room):
                if not room.online_users:
                    if not room.static:
                        self.server.log.info("No users deleteing Room: %s" % (room.name))
                        self.session.delete(room)
                        self.conn.room = None
            roomspacket = models.Room.smo_list(self.session, self.active_users)
            for conn in self.server.connections:
                if conn.room == None:
                    conn.send(roomspacket)
                    self.server.send_user_list_lobby(conn, self.session)

        if not self.conn.spectate:
            for user in self.active_users:
                user.status = status_mapping.get(
                    self.packet["action"],
                    models.UserStatus.room_selection
                ).value

        if self.conn.room:
            self.server.send_user_list(self.room)
