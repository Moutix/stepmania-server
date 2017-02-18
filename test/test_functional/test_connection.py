""" Module to test the connections of client """

from smserver.smutils.smpacket import smpacket

from test.test_functional.helper import FunctionalTest

class ConnectionTest(FunctionalTest):
    """ Test the client connection """

    def test_addclient(self):
        """ Test adding a client """

        self.server.add_connection(self.client_bin)
        self.server.add_connection(self.client_json)

        self.assertIn(self.client_bin, self.server.connections)
        self.assertIsNotNone(self.bin_connection)
        self.assertEqual(self.client_bin.ip, self.bin_connection.ip)
        self.assertEqual(self.client_bin.port, self.bin_connection.port)

        self.assertIn(self.client_json, self.server.connections)
        self.assertIsNotNone(self.json_connection)
        self.assertEqual(self.client_json.ip, self.json_connection.ip)
        self.assertEqual(self.client_json.port, self.json_connection.port)

    def test_hello_binary(self):
        """ Test sending hello data to BIN client """
        self.client_bin.on_data(
            smpacket.SMPacketClientNSCHello(name="stepmania-binary", version=40).binary
        )

        self.assertEqual(self.client_bin.client_name, "stepmania-binary")
        self.assertEqual(self.client_bin.client_version, 40)

        self.assertBinSend(smpacket.SMPacketServerNSCHello)

    def test_hello_json(self):
        """ Test sending hello data to JSON client"""

        self.client_json.on_data(
            smpacket.SMPacketClientNSCHello(name="stepmania-json", version=41).json
        )

        self.assertEqual(self.client_json.client_name, "stepmania-json")
        self.assertEqual(self.client_json.client_version, 41)

        self.assertJSONSend(smpacket.SMPacketServerNSCHello)
