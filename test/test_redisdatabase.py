""" Test redis database module """

import unittest

from smserver import redis_database

class RedisDatabaseTest(unittest.TestCase):
    """ Test redis database module module """

    def test_connection_fail(self):
        """ Test redis connection fail """

        with self.assertRaises(ConnectionError):
            redis_database.RedisDataBase(url="redis://bla:6379")

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
