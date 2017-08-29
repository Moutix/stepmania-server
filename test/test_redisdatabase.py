""" Test redis database module """

import unittest
import mock

from smserver import redis_database

class RedisDatabaseTest(unittest.TestCase):
    """ Test redis database module module """

    @mock.patch("redis.ConnectionPool")
    def test_connection_fail(self, conn):
        """ Test redis connection fail """

        conn.from_url.side_effect = ConnectionError

        with self.assertRaises(ConnectionError):
            redis_database.RedisDataBase(url="invalid url")

    def test_new_connection(self):
        """ Test getting new redis connection """

        if not redis_database.is_available():
            self.skipTest("Redis not configured")

        conn = redis_database.new_connection()

        self.assertEqual(conn.get("test_var"), None)
        conn.set("test_var", "b")
        self.assertEqual(conn.get("test_var"), "b")
        conn.delete("test_var")
        self.assertEqual(conn.get("test_var"), None)
