""" Module to test the song_stat model """

import datetime

from test.factories.song_stat_factory import SongStatFactory
from test.factories.user_factory import UserFactory
from test import utils

class SongStatTest(utils.DBTest):
    """ test SongStat model"""

    def test_lit_difficulty(self):
        """ Test lit_difficulty property """
        song_stat = SongStatFactory(difficulty=0)
        self.assertEqual(song_stat.lit_difficulty, "BEGINNER")

        song_stat = SongStatFactory(difficulty=1)
        self.assertEqual(song_stat.lit_difficulty, "EASY")

        song_stat = SongStatFactory(difficulty=2)
        self.assertEqual(song_stat.lit_difficulty, "MEDIUM")

        song_stat = SongStatFactory(difficulty=3)
        self.assertEqual(song_stat.lit_difficulty, "HARD")

        song_stat = SongStatFactory(difficulty=4)
        self.assertEqual(song_stat.lit_difficulty, "EXPERT")

        song_stat = SongStatFactory(difficulty=67)
        self.assertEqual(song_stat.lit_difficulty, "67")

    def test_full_difficulty(self):
        """ Test full_difficulty property """
        song_stat = SongStatFactory(difficulty=0, feet=4)
        self.assertEqual(song_stat.full_difficulty, "BEGINNER (4)")

        song_stat = SongStatFactory(difficulty=3, feet=78)
        self.assertEqual(song_stat.full_difficulty, "HARD (78)")

    def test_lit_grade(self):
        """ Test lit_difficulty property """
        song_stat = SongStatFactory(grade=0)
        self.assertEqual(song_stat.lit_grade, "AAAA")

        song_stat = SongStatFactory(grade=1)
        self.assertEqual(song_stat.lit_grade, "AAA")

        song_stat = SongStatFactory(grade=3)
        self.assertEqual(song_stat.lit_grade, "A")

        song_stat = SongStatFactory(grade=4)
        self.assertEqual(song_stat.lit_grade, "B")

        song_stat = SongStatFactory(grade=6)
        self.assertEqual(song_stat.lit_grade, "D")

    def test_pretty_result(self):
        """ Test pretty_result property """
        date = datetime.datetime(2017, 10, 13, 11, 42)

        song_stat = SongStatFactory(
            difficulty=3, #HARD
            feet=9,
            grade=3, #A
            user=UserFactory(name="José Prout"),
            percentage=78.327,
            created_at=date
        )

        self.assertEqual(
            song_stat.pretty_result(),
            r"HARD (9): José Prout A (78.33%) on 13/10/17"
        )
