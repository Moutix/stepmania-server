""" Module to test the login of client """

from smserver import models
from smserver import stepmania_controller
from smserver.smutils.smpacket import smpacket

from test.test_functional.helper import UserFunctionalTest

class ServerTest(UserFunctionalTest):
    """ Test the client login """

    def test_client_bin_room_creation(self):
        """ First room creation """

        self.client_bin.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientCreateRoom(
                type=1,
                title="Room client-bin",
                description="test room",
                password="password")
        ).binary)

        room = self.session.query(models.Room).filter_by(name="Room client-bin").first()

        self.assertEqual(self.bin_connection.room, room)
        self.assertEqual(room.description, "test room")

        self.assertEqual(self.user_bin1.room, room)
        self.assertEqual(self.user_bin2.room, room)

        self.assertEqual(self.user_bin1.level(room.id), 10)
        self.assertEqual(self.user_bin2.level(room.id), 10)

    def test_client_bin_user_screen(self):
        """ Test client bin go to room_selection """

        self.client_bin.on_data(smpacket.SMPacketClientNSSCSMS(
            action=7
        ).binary)

        packet = self.get_smpacket_in(smpacket.SMPacketServerNSSMONL, self.client_bin.packet_send)
        self.assertIsNotNone(packet)
        self.assertIsInstance(packet["packet"], smpacket.SMOPacketServerRoomUpdate)

        self.assertEqual(self.user_bin1.status, models.UserStatus.room_selection.value)
        self.assertEqual(self.user_bin2.status, models.UserStatus.room_selection.value)



    def test_json_room_info(self):
        """ Display room information in room selection """
        self.test_client_bin_room_creation()

        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientRoomInfo(
                room="Room client-bin")
        ).json)

        packet = self.get_smpacket_in(smpacket.SMPacketServerNSSMONL, self.client_json.packet_send)

        self.assertIsNotNone(packet)

        self.assertIsInstance(packet["packet"], smpacket.SMOPacketServerRoomInfo)

        self.assertEqual(packet["packet"]["num_players"], 2)
        self.assertIn("clientbin-user1", packet["packet"]["players"])
        self.assertIn("clientbin-user2", packet["packet"]["players"])


    def test_json_fail_create_room_name_already_taken(self):
        """ Json client create a room that already exist """

        self.test_client_bin_room_creation()

        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientCreateRoom(
                type=1,
                title="Room client-bin",
                description="test room",
                password="password")
        ).json)

        self.assertIsNone(self.json_connection.room)
    def test_json_fail_enter_room_wrong_password(self):
        """ Json client try to enter in a room with the wrong password """
        self.test_client_bin_room_creation()

        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientEnterRoom(
                enter=1,
                room="Room client-bin",
                password="wrong password"
            )
        ).json)

        self.assertIsNone(self.json_connection.room)

    def test_json_enter_room(self):
        """ Json client enter in the client-bin room """

        self.test_client_bin_room_creation()

        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientEnterRoom(
                enter=1,
                room="Room client-bin",
                password="password"
            )
        ).json)

        room = self.session.query(models.Room).filter_by(name="Room client-bin").first()
        user = self.user_json1

        self.assertEqual(self.json_connection.room, room)
        self.assertEqual(user.room, room)
        self.assertEqual(user.level(room.id), 1)

    def test_client_json_room_creation(self):
        """ Json client create a new room, and exit the client-bin room """

        self.test_json_enter_room()

        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientCreateRoom(
                type=1,
                title="Room client-json",
                description="test room",
                password="password")
        ).json)

        room = self.session.query(models.Room).filter_by(name="Room client-json").first()
        user = self.user_json1

        self.assertEqual(self.json_connection.room, room)
        self.assertEqual(room.description, "test room")

        self.assertEqual(user.room, room)

        self.assertEqual(user.level(room.id), 10)

    def test_bin_enter_room(self):
        """ Bin Client enter in json room and exit the other """

        self.test_client_json_room_creation()

        self.client_bin.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientEnterRoom(
                enter=1,
                room="Room client-json",
                password="password")
        ).binary)

        room = self.session.query(models.Room).filter_by(name="Room client-json").first()
        user1 = self.user_bin1
        user2 = self.user_bin2

        self.assertEqual(self.bin_connection.room, room)

        self.assertEqual(user1.room, room)
        self.assertEqual(user2.room, room)

        self.assertEqual(user1.level(room.id), 1)
        self.assertEqual(user2.level(room.id), 1)

    def test_bin_select_song_1(self):
        """ First time song selection, ask if everybody have the song """
        self.test_bin_enter_room()

        packet = smpacket.SMPacketClientNSCRSG(
            usage=2,
            song_title="Title",
            song_artist="Artist",
        )
        self.client_bin.on_data(packet.binary)

        controller = stepmania_controller.StepmaniaController(
            self.server, self.client_bin, packet, self.session
        )

        song = self.session.query(models.Song).filter_by(
            title="Title",
            artist="Artist",
            subtitle=""
        ).first()

        self.assertIsNotNone(song)

        self.assertNotEqual(controller.room.status, 2)
        self.assertEqual(controller.conn.song, song.id)
        self.assertFalse(controller.conn.ingame)
        self.assertIn(self.get_smpacket_in(smpacket.SMPacketServerNSCRSG, self.client_bin.packet_send)["usage"], (0, 1))
        self.assertIn(self.get_smpacket_in(smpacket.SMPacketServerNSCRSG, self.client_json.packet_send)["usage"],  (0, 1))

    def test_bin_select_song_2(self):
        """ Client bin reselect the same song """

        self.test_bin_select_song_1()

        packet = smpacket.SMPacketClientNSCRSG(
            usage=2,
            song_title="Title",
            song_artist="Artist",
        )
        self.client_bin.on_data(packet.binary)

        controller = stepmania_controller.StepmaniaController(
            self.server, self.client_bin, packet, self.session
        )

        song = self.session.query(models.Song).filter_by(
            title="Title",
            artist="Artist",
            subtitle=""
        ).first()

        self.assertIsNotNone(song)

        self.assertFalse(self.client_bin.wait_start)
        self.assertFalse(self.client_json.wait_start)

        self.assertEqual(controller.room.status, 2)
        self.assertEqual(controller.room.active_song, song)
        self.assertIn(self.get_smpacket_in(smpacket.SMPacketServerNSCRSG, self.client_bin.packet_send)["usage"], (2, 3))
        self.assertIn(self.get_smpacket_in(smpacket.SMPacketServerNSCRSG, self.client_json.packet_send)["usage"], (2, 3))

    def test_watcher_game_start(self):
        """
            Watcher run all the script we don't start the song since no NSCGSR
            packet has been sent
        """
        self.test_bin_select_song_2()

        self.server.watcher.force_run()

        self.assertIsNone(self.get_smpacket_in(smpacket.SMPacketServerNSCGSR, self.client_bin.packet_send))

    def test_client_bin_game_start_request(self):
        """
            Client-bin send a game start request, wait for client-json
        """
        self.test_watcher_game_start()

        packet = smpacket.SMPacketClientNSCGSR(
            first_player_feet=8,
            second_player_feet=9,
            first_player_difficulty=3,
            second_player_difficulty=4,
            start_position=0,
            song_title="Title",
            song_artist="Artist",
        )

        self.client_bin.on_data(packet.binary)

        songstats = self.client_bin.songstats

        self.assertTrue(self.client_bin.wait_start)
        self.assertFalse(self.client_bin.ingame)

        self.assertEqual(songstats[0]["difficulty"], 3)
        self.assertEqual(songstats[1]["difficulty"], 4)

    def test_client_json_game_start_request(self):
        """
            Client-json send a game start request, start the game
        """
        self.test_client_bin_game_start_request()

        packet = smpacket.SMPacketClientNSCGSR(
            first_player_feet=5,
            first_player_difficulty=2,
            start_position=0,
            song_title="Title",
            song_artist="Artist",
        )

        self.client_json.on_data(packet.json)

        self.assertFalse(self.client_bin.wait_start)
        self.assertFalse(self.client_json.wait_start)
        self.assertTrue(self.client_bin.ingame)
        self.assertTrue(self.client_json.ingame)


    def test_client_bin_game_status_update(self):
        """ Client-bin send a game status update package """

        self.test_client_json_game_start_request()
        packet = smpacket.SMPacketClientNSCGSU(
            player_id=0,
            step_id=4,
            grade=3,
            score=50000,
            combo=1,
            health=50,
            offset=20000,
        )

        self.client_bin.on_data(packet.binary)

        songstats = self.client_bin.songstats

        self.assertEqual(len(songstats[0]["data"]), 1)
        self.assertEqual(songstats[0]["data"][0]["stepid"], 4)
        self.assertEqual(songstats[0]["data"][0]["grade"], 3)
        self.assertEqual(songstats[0]["data"][0]["score"], 50000)
        self.assertEqual(songstats[0]["data"][0]["combo"], 1)
        self.assertEqual(songstats[0]["data"][0]["health"], 50)

        self.client_bin.on_data(packet.binary)
        self.assertEqual(len(songstats[0]["data"]), 2)

    def test_client_bin_game_over(self):
        """ Test sending a game over packet for client bin """

        self.test_client_bin_game_status_update()

        packet = smpacket.SMPacketClientNSCGON()
        self.client_bin.on_data(packet.binary)

        self.assertFalse(self.client_bin.ingame)
        self.assertEqual(self.client_bin.songstats[0]["data"], [])
        self.assertEqual(self.client_bin.songstats[1]["data"], [])
        self.assertIsNone(self.client_bin.song)

        songstats = list(self.session.query(models.SongStat).filter_by(user=self.user_bin1))
        self.assertEqual(len(songstats), 1)

        self.assertEqual(songstats[0].score, 50000)
        self.assertEqual(songstats[0].grade, 3)
        self.assertEqual(songstats[0].max_combo, 1)

    def test_client_bin_disconnect(self):
        """ Test client bin disconnection """

        self.test_client_bin_game_over()

        self.client_bin.close()

        self.assertEqual(self.user_bin1.online, False)
        self.assertIsNone(self.user_bin1.room)
        self.assertEqual(self.user_bin2.online, False)
        self.assertIsNone(self.user_bin2.room)
        self.assertEqual(self.user_json1.online, True)
