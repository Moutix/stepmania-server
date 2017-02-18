""" Login controller """

from smserver.smutils.smpacket import smpacket
from smserver.smutils.smpacket import smcommand
from smserver.stepmania_controller import StepmaniaController
from smserver.resources import user_resource
from smserver import models
from smserver import exceptions
from smserver import __version__

class LoginController(StepmaniaController):
    """ Controller use to manage SMO LOGIN packet """

    command = smcommand.SMOClientCommand.LOGIN
    require_login = False

    def handle(self):
        """ Handle a SMO login packet """

        resource = user_resource.UserResource(self.server, self.conn.token, self.session)

        if self.server.config.auth["autocreate"]:
            login_func = resource.login_or_create
        else:
            login_func = resource.login

        try:
            user = login_func(self.packet["username"], self.packet["password"])
        except exceptions.Forbidden as err:
            self.send(smpacket.SMPacketServerNSSMONL(
                packet=smpacket.SMOPacketServerLogin(
                    approval=1,
                    text=err.message
                )
            ))
            return

        try:
            resource.connect(user, pos=self.packet["player_number"])
        except exceptions.Unauthorized as err:
            self.send(smpacket.SMPacketServerNSSMONL(
                packet=smpacket.SMOPacketServerLogin(
                    approval=1,
                    text=err.message
                )
            ))
            return

        nb_onlines = models.User.nb_onlines(self.session)
        max_users = self.server.config.server.get("max_users", -1)

        if not self.users:
            self._send_server_resume(nb_onlines, max_users)

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=smpacket.SMOPacketServerLogin(
                approval=0,
                text="Player %s successfully login" % self.packet["username"]
            )
        ))

        self.send(models.Room.smo_list(self.session, self.active_users))

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
