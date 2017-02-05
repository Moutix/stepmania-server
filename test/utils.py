""" Utils module for test """

import unittest

from test import common

class DBTest(unittest.TestCase):
    """ Base class for DBTest"""

    def setUp(self):
        # Prepare a new, clean session
        self.session = common.db.session()

    def tearDown(self):
        # Rollback the session => no changes to the database
        common.db.recreate_tables()
        # Remove it, so that the next test gets a new Session()
        common.db.session.remove()
