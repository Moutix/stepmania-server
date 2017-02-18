""" Module to test ban model """

import datetime

import mock

from smserver import models

from test.factories.ban_factory import BanFactory
from test.factories.user_factory import UserFactory
from test.factories.room_factory import RoomFactory
from test import utils

class BanTest(utils.DBTest):
    """ test Ban model"""


    def test_ban_repr(self):
        """ Test Display Ban """

        ban = BanFactory(ip="8.8.8.8")

        self.assertEqual(str(ban), "<Ban #1 (ip='8.8.8.8', user_id='None', room_id='None'>")

    def test_find_ban(self):
        """ Test to find a ban """

        ban = BanFactory(ip="8.8.8.8")
        self.assertEqual(models.Ban.find_ban(session=self.session, ip="8.8.8.8"), ban)

        ban.end_at = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        self.assertEqual(models.Ban.find_ban(session=self.session, ip="8.8.8.8"), ban)

        ban.end_at = datetime.datetime.utcnow()
        self.assertIsNone(models.Ban.find_ban(session=self.session, ip="8.8.8.8"))

        room = RoomFactory()
        ban.room = room
        ban.end_at = None

        self.assertIsNone(models.Ban.find_ban(session=self.session, ip="8.8.8.8"))
        self.assertEqual(
            models.Ban.find_ban(
                session=self.session,
                ip="8.8.8.8",
                room_id=room.id),
            ban
        )

        user = UserFactory()

        ban = BanFactory(user=user)
        self.assertEqual(
            models.Ban.find_ban(session=self.session, user_id=user.id),
            ban
        )
        ban.room = room

        self.assertIsNone(
            models.Ban.find_ban(session=self.session, user_id=user.id)
        )
        self.assertEqual(
            models.Ban.find_ban(
                session=self.session,
                user_id=user.id,
                room_id=room.id
            ),
            ban
        )

    @mock.patch("smserver.models.ban.Ban.find_ban")
    def test_is_ban(self, find_ban):
        """ Test if somenone is ban """

        ban = BanFactory()
        find_ban.return_value = ban
        self.assertTrue(models.Ban.is_ban(self.session, ip="8.8.8.8"))
        find_ban.assert_called_once()

        find_ban.reset_mock()
        find_ban.return_value = None
        self.assertFalse(models.Ban.is_ban(self.session, ip="8.8.8.8"))
        find_ban.assert_called_once()

    def test_unban(self):
        """ Test unban someone """

        BanFactory(ip="8.8.8.8")

        self.assertTrue(models.Ban.is_ban(self.session, ip="8.8.8.8"))
        self.assertTrue(models.Ban.unban(self.session, ip="8.8.8.8"))
        self.assertFalse(models.Ban.unban(self.session, ip="8.8.8.8"))
        self.assertFalse(models.Ban.is_ban(self.session, ip="8.8.8.8"))

    def test_ban(self):
        """ test to ban someone """

        ban = models.Ban.ban(self.session, ip="8.8.8.8")
        self.assertEqual(ban.ip, "8.8.8.8")
        self.assertIsNone(ban.end_at)
        self.assertIsNone(ban.user_id)
        self.assertIsNone(ban.room_id)

        self.assertEqual(models.Ban.ban(self.session, ip="8.8.8.8", duration=50), ban)
        self.assertGreater(ban.end_at, datetime.datetime.utcnow())

        self.assertEqual(models.Ban.ban(self.session, ip="8.8.8.8", fixed=True), ban)
        self.assertIsNone(ban.end_at)
        self.assertTrue(ban.fixed)
