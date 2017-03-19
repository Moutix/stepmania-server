""" Module to test the chat message between client """

import time

from smserver import models
from smserver.smutils.smpacket import smpacket

from test.test_functional.helper import UserFunctionalTest

class ChatTest(UserFunctionalTest):
    """ Test the chat """

    def setUp(self):
        super().setUp()

        # Client bin create a room
        self.client_bin.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientCreateRoom(
                type=1,
                title="ChatRoom",
                description="test chat room",
                password="password")
        ).binary)

        # Client JSON enter in his room
        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientEnterRoom(
                enter=1,
                room="ChatRoom",
                password="password"
            )
        ).json)

        self.client_bin.packet_send = []
        self.client_json.packet_send = []
        self.server.listener.start()

    def tearDown(self):
        self.server.listener.stop()
        self.server.listener.join()
        super().tearDown()

    @property
    def room(self):
        """ Return the room use for the chat test """

        return self.session.query(models.Room).filter_by(name="ChatRoom").first()

    def test_bin_client_send_message(self):
        """ Bin client send a new message in the chat """

        self.client_bin.on_data(smpacket.SMPacketClientNSCCM(
            message="coucou",
        ).binary)

        time.sleep(0.02)
        self.assertBinSend(smpacket.SMPacketServerNSCCM)
        self.assertJSONSend(smpacket.SMPacketServerNSCCM)

    def test_json_client_send_message(self):
        """ Bin client send a new message in the chat """

        self.client_json.on_data(smpacket.SMPacketClientNSCCM(
            message="coucou",
        ).json)

        time.sleep(0.02)
        self.assertBinSend(smpacket.SMPacketServerNSCCM)
        self.assertJSONSend(smpacket.SMPacketServerNSCCM)

    def test_json_invalid_command(self):
        """ Json client send an invalid command """

        self.client_json.on_data(smpacket.SMPacketClientNSCCM(
            message="/invalid_command bla",
        ).json)
        self.assertJSONSend(smpacket.SMPacketServerNSCCM)
        packet = self.get_smpacket_in(smpacket.SMPacketServerNSCCM, self.client_json.packet_send)

        self.assertRegex(packet["message"], "Unknown command")

    def test_json_ban_user(self):
        """ Json client try to ban the bin client (unauthorized) """

        self.client_json.on_data(smpacket.SMPacketClientNSCCM(
            message="/ban client_bin",
        ).json)
        self.assertJSONSend(smpacket.SMPacketServerNSCCM)
        packet = self.get_smpacket_in(smpacket.SMPacketServerNSCCM, self.client_json.packet_send)

        self.assertRegex(packet["message"], "Unauthorized")

    def test_bin_ban_invalid_name_from_room(self):
        """ Bin client ban an invalid user from his room """

        self.client_bin.on_data(smpacket.SMPacketClientNSCCM(
            message="/ban invalid_user",
        ).binary)
        self.assertBinSend(smpacket.SMPacketServerNSCCM)
        packet = self.get_smpacket_in(smpacket.SMPacketServerNSCCM, self.client_bin.packet_send)

        self.assertRegex(packet["message"], "Unknown user")

    def test_bin_ban_json_from_room(self):
        """ Bin client ban the JSON client from his room """

        self.client_bin.on_data(smpacket.SMPacketClientNSCCM(
            message="/ban %s" % self.user_json1.name,
        ).binary)
        time.sleep(0.02)
        self.assertBinSend(smpacket.SMPacketServerNSCCM)
        packet = self.get_smpacket_in(smpacket.SMPacketServerNSCCM, self.client_bin.packet_send)

        json_user = self.user_json1

        self.assertRegex(packet["message"], "ban.+%s" % json_user.name)

        self.assertIsNone(json_user.room)

        self.assertTrue(
            models.Ban.is_ban(
                self.session,
                user_id=json_user.id,
                room_id=self.room.id
            )
        )

    def test_bin_kick_json_from_room(self):
        """ Bin client ban the JSON client from his room """

        self.client_bin.on_data(smpacket.SMPacketClientNSCCM(
            message="/kick %s" % self.user_json1.name,
        ).binary)
        time.sleep(0.02)
        self.assertBinSend(smpacket.SMPacketServerNSCCM)
        packet = self.get_smpacket_in(smpacket.SMPacketServerNSCCM, self.client_bin.packet_send)

        json_user = self.user_json1

        self.assertRegex(packet["message"], "kick.+%s" % json_user.name)

        self.assertIsNone(json_user.room)

        self.assertFalse(
            models.Ban.is_ban(
                self.session,
                user_id=json_user.id,
                room_id=self.room.id
            )
        )
