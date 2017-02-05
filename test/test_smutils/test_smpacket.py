""" Test smpacket.SMPacket module """

import unittest

from smserver.smutils import smpacket

class SMPacketTest(unittest.TestCase):
    """ Test smpacket.SMPacket class """

    def test_nsgsr_packet(self):
        """ Test encoding and decoding a nsgsr packet """
        packet = smpacket.SMPacket.new(
            smpacket.SMClientCommand.NSCGSR,
            second_player_feet=8,
            first_player_feet=12,
            song_title="Wouhou whouhouhou",
            song_subtitle="super sous titer"
        )

        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.parse_binary(packet.binary).binary
        )
        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.from_("json", packet.to_("json")).binary
        )

    def test_smonl_room_info_packet(self):
        """ Test encoding and decoding a smpacket.SMO ROOMINFO packet"""

        packet = smpacket.SMPacket.new(
            smpacket.SMServerCommand.NSSMONL,
            packet=smpacket.SMOPacketServer.new(
                smpacket.SMOServerCommand.ROOMINFO,
                song_title="song_title",
                num_players=3,
                players=["bidule", "machin", "truc"]
            )
        )

        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.parse_binary(packet.binary).binary
        )
        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.from_("json", packet.to_("json")).binary
        )

    def test_nscgon_packet(self):
        """ Test encoding and decoding a NSCGON packet """
        packet = smpacket.SMPacket.new(
            smpacket.SMServerCommand.NSCGON,
            nb_players=3,
            ids=[5, 2, 8],
            scores=[1550, 1786, 1632],
        )

        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.parse_binary(packet.binary).binary
        )
        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.from_("json", packet.to_("json")).binary
        )

    def test_nsccuul_packet(self):
        """ Test nsccuul packet """

        packet = smpacket.SMPacket.new(
            smpacket.SMServerCommand.NSCCUUL,
            max_players=255,
            nb_players=5,
            players=[{"status": 5, "name": "machin"}, {"status": 1, "name": "bidule"}]
        )

        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.parse_binary(packet.binary).binary
        )
        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.from_("json", packet.to_("json")).binary
        )

    def test_nscgsu_packet(self):
        """ Test encoding and decoding a NSCGCU packet """
        packet = smpacket.SMPacket.new(
            smpacket.SMServerCommand.NSCGSU,
            section=1,
            nb_players=3,
            options=[1, 3, 5]
        )

        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.parse_binary(packet.binary).binary
        )
        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.from_("json", packet.to_("json")).binary
        )

    def test_smo_roomupdate_type0_packet(self):
        """ Test encoding and decoding a smpacket.SMO ROOMUPDATE packet (type 0)"""

        packet = smpacket.SMPacket.new(
            smpacket.SMServerCommand.NSSMONL,
            packet=smpacket.SMOPacketServer.new(
                smpacket.SMOServerCommand.ROOMUPDATE,
                type=0,
                room_title="Super Room",
                subroom=1,
                room_description="description de la salle",
            )
        )
        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.parse_binary(packet.binary).binary
        )
        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.from_("json", packet.to_("json")).binary
        )

    def test_smo_room_update_type1_packet(self):
        """ Test encoding and decoding a smpacket.SMO ROOMUPDATE packet (type 1)"""

        packet = smpacket.SMPacket.new(
            smpacket.SMServerCommand.NSSMONL,
            packet=smpacket.SMOPacketServer.new(
                smpacket.SMOServerCommand.ROOMUPDATE,
                type=1,
                nb_rooms=3,
                rooms=[
                    {"title": "salle1", "description": "description1"},
                    {"title": "salle2", "description": "description2"},
                    {"title": "salle3", "description": "description3"},
                ],
                room_description="description de la salle",
            )
        )

        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.parse_binary(packet.binary).binary
        )
        self.assertEqual(
            packet.binary,
            smpacket.SMPacket.from_("json", packet.to_("json")).binary
        )
