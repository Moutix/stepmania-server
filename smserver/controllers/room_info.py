""" Room info controller module """

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models

class RoomInfoController(StepmaniaController):
    """ Room Info controller """

    command = smpacket.SMOClientCommand.ROOMINFO
    require_login = True

    def handle(self):
        room = self.session.query(models.Room).filter_by(name=self.packet["room"]).first()
        if not room:
            self.log.info("Room %s don't exist", self.packet["room"])
            return

        self.send(room.room_info)
