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

        time.sleep(0.2)
        self.assertBinSend(smpacket.SMPacketServerNSCCM)
        self.assertJSONSend(smpacket.SMPacketServerNSCCM)

    def test_json_client_send_message(self):
        """ Bin client send a new message in the chat """

        self.client_json.on_data(smpacket.SMPacketClientNSCCM(
            message="coucou",
        ).json)

        time.sleep(0.2)
        self.assertBinSend(smpacket.SMPacketServerNSCCM)
        self.assertJSONSend(smpacket.SMPacketServerNSCCM)
