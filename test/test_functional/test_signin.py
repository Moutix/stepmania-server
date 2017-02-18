""" Module to test the login of client """

from smserver import models
from smserver.smutils.smpacket import smpacket

from test.test_functional.helper import ConnectedFunctionalTest

class SigninTest(ConnectedFunctionalTest):
    """ Test the client login """

    def test_client_bin_sign_in_one_user(self):
        """ First time login for clientbin-user1, the user is created """
        self.client_bin.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientbin-user1",
                password="testtest",
                player_number=0
            )
        ).binary)

        user = self.session.query(models.User).filter_by(name="clientbin-user1").first()

        self.assertIsNotNone(user)
        self.assertTrue(user.online)
        self.assertEqual(user.last_ip, self.client_bin.ip)
        self.assertIsNone(user.room)
        self.assertEqual(user.pos, 0)
        self.assertIn(user, self.bin_connection.users)

    def test_client_bin_sign_in_wrong_password(self):
        """ Login with a wrong password """

        self.test_client_bin_sign_in_one_user()

        self.client_bin.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientbin-user1",
                password="wrong_password",
                player_number=1
            )
        ).binary)

        user = self.session.query(models.User).filter_by(name="clientbin-user1").first()

        self.assertIsNotNone(user)
        self.assertTrue(user.online)
        self.assertEqual(user.last_ip, self.client_bin.ip)
        self.assertIsNone(user.room)
        self.assertEqual(user.pos, 0)

        self.assertIn(user, self.bin_connection.users)

    def test_client_bin_sign_in_second_user(self):
        """ First time login for clientbin-user2, the user is created """

        self.test_client_bin_sign_in_one_user()

        self.client_bin.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientbin-user2",
                password="testtest",
                player_number=1
            )
        ).binary)

        user = self.session.query(models.User).filter_by(name="clientbin-user2").first()

        self.assertTrue(user.online)
        self.assertEqual(user.last_ip, self.client_bin.ip)
        self.assertIsNone(user.room)
        self.assertEqual(user.pos, 1)

        self.assertIn(user, self.bin_connection.users)

    def test_client_bin_logout_user(self):
        """ Player select only one profile, we disconnect the player 1"""
        self.test_client_bin_sign_in_one_user()
        self.test_client_bin_sign_in_second_user()

        self.client_bin.on_data(
            smpacket.SMPacketClientNSCSU(
                player_id=0,
                nb_players=1,
                player_name="name"
            ).binary
        )

        user2 = self.session.query(models.User).filter_by(name="clientbin-user2").first()
        self.assertFalse(user2.online)

        user1 = self.session.query(models.User).filter_by(name="clientbin-user1").first()
        self.assertTrue(user1.online)

    def test_client_bin_reconnect_user(self):
        """ Player select only two profile, we reconnect the offline player """

        self.test_client_bin_sign_in_one_user()
        self.test_client_bin_sign_in_second_user()
        self.test_client_bin_logout_user()

        self.client_bin.on_data(
            smpacket.SMPacketClientNSCSU(
                player_id=0,
                nb_players=2,
                player_name="name"
            ).binary
        )

        user2 = self.session.query(models.User).filter_by(name="clientbin-user2").first()
        self.assertTrue(user2.online)

        user1 = self.session.query(models.User).filter_by(name="clientbin-user1").first()
        self.assertTrue(user1.online)

    def test_json_sign_in_one_user(self):
        """ First time login for clientjson-user1, the user is created """
        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientjson-user1",
                password="testtest",
                player_number=0
            )
        ).json)

        user = self.session.query(models.User).filter_by(name="clientjson-user1").first()

        self.assertIsNotNone(user)
        self.assertTrue(user.online)
        self.assertEqual(user.last_ip, self.client_json.ip)
        self.assertIsNone(user.room)
        self.assertEqual(user.pos, 0)

        self.assertIn(user, self.json_connection.users)


    def test_json_sign_in_with_same_user(self):
        """ Player reconnect the same user already logued in (in another pos) """

        self.test_json_sign_in_one_user()

        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientjson-user1",
                password="testtest",
                player_number=1
            )
        ).json)

        user = self.session.query(models.User).filter_by(name="clientjson-user1").first()

        self.assertTrue(user.online)
        self.assertEqual(user.last_ip, self.client_json.ip)
        self.assertIsNone(user.room)
        self.assertEqual(user.pos, 1)

        self.assertIn(user, self.json_connection.users)
        self.assertEqual(len(self.json_connection.users), 1)

    def test_json_sign_in_second_user(self):
        """ A second user sign in the free pos"""

        self.test_json_sign_in_with_same_user()

        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientjson-user2",
                password="testtest",
                player_number=0
            )
        ).json)

        user = self.session.query(models.User).filter_by(name="clientjson-user2").first()

        self.assertTrue(user.online)
        self.assertEqual(user.last_ip, self.client_json.ip)
        self.assertIsNone(user.room)
        self.assertEqual(user.pos, 0)

        self.assertIn(user, self.json_connection.users)

        self.assertEqual(len(self.json_connection.users), 2)

    def test_json_sign_in_third_user(self):
        """ A third user connect in a pos already taken """

        self.test_json_sign_in_with_same_user()
        self.test_json_sign_in_second_user()

        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientjson-user3",
                password="testtest",
                player_number=1
            )
        ).json)

        user3 = self.session.query(models.User).filter_by(name="clientjson-user3").first()
        user1 = self.session.query(models.User).filter_by(name="clientjson-user1").first()

        self.assertTrue(user3.online)
        self.assertEqual(user3.last_ip, self.client_json.ip)
        self.assertIsNone(user3.room)
        self.assertEqual(user3.pos, 1)

        self.assertIn(user3, self.json_connection.users)

        self.assertEqual(len(self.json_connection.users), 3)
        self.assertEqual(len(self.json_connection.active_users), 2)

        self.assertFalse(user1.online)
