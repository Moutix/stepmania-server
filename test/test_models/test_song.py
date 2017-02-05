""" Module to test the song model """

from smserver import models


from test.factories.song_factory import SongFactory
from test.factories.song_stat_factory import SongFinishFactory
from test import utils

class SongTest(utils.DBTest):
    """ test Song model"""

    def test_time_played(self):
        """ Test the number of song_stat element """

        song = SongFactory()
        self.session.commit()
        self.assertEqual(song.time_played, 0)
        for _ in range(5):
            SongFinishFactory(song=song)
        self.session.commit()

        self.assertEqual(song.time_played, 5)

    def test_fullname(self):
        """ Test getting the fullname of a song """

        song = SongFactory(title="Title", artist="Artist")
        self.assertEqual(song.fullname, "Title (Artist)")

    def test_best_scores(self):
        """ Test getting the best score of the song for each feet """

        song = SongFactory()
        self.assertEqual(song.best_scores, [])

        data = (
            (45000, 3),
            (42000, 3),
            (41000, 3),
            (100, 5),
            (60, 9),
            (890, 9),
        )

        for score, feet in data:
            SongFinishFactory(song=song, score=score, feet=feet)

        best_scores = song.best_scores
        self.assertEqual(len(best_scores), 3)
        self.assertEqual(best_scores[0].feet, 3)
        self.assertEqual(best_scores[0].score, 45000)

        self.assertEqual(best_scores[1].feet, 5)
        self.assertEqual(best_scores[1].score, 100)

        self.assertEqual(best_scores[2].feet, 9)
        self.assertEqual(best_scores[2].score, 890)

    def test_highscores(self):
        """ Return the highest score of this song """

        song = SongFactory()
        self.assertEqual(list(song.highscores(4)), [])
        self.assertEqual(list(song.highscores()), [])

        data = (
            (45000, 3),
            (42000, 3),
            (41000, 3),
            (100, 5),
            (60, 9),
            (890, 9),
        )

        for score, feet in data:
            SongFinishFactory(song=song, score=score, feet=feet)

        self.assertEqual(len(list(song.highscores())), 6)
        self.assertEqual(list(song.highscores())[0].score, 45000)
        self.assertEqual(list(song.highscores())[-1].score, 60)


        self.assertEqual(len(list(song.highscores(9))), 2)
        self.assertEqual(list(song.highscores(9))[0].score, 890)

    def test_best_score(self):
        """ Test getting the best score of a song """

        song = SongFactory()
        self.assertEqual(song.best_score(4), None)
        self.assertEqual(song.best_score(), None)

        data = (
            (45000, 3),
            (42000, 3),
            (41000, 3),
            (100, 5),
            (60, 9),
            (890, 9),
        )

        for score, feet in data:
            SongFinishFactory(song=song, score=score, feet=feet)

        self.assertEqual(song.best_score().score, 45000)
        self.assertEqual(song.best_score(3).score, 45000)
        self.assertEqual(song.best_score(5).score, 100)
        self.assertEqual(song.best_score(9).score, 890)
        self.assertEqual(song.best_score(78), None)

    def test_best_score_value(self):
        """ Test getting the best score value of a song """

        song = SongFactory()
        self.assertEqual(song.best_score_value(4), None)
        self.assertEqual(song.best_score_value(), None)

        data = (
            (45000, 3),
            (42000, 3),
            (41000, 3),
            (100, 5),
            (60, 9),
            (890, 9),
        )

        for score, feet in data:
            SongFinishFactory(song=song, score=score, feet=feet)

        self.assertEqual(song.best_score_value(), 45000)
        self.assertEqual(song.best_score_value(3), 45000)
        self.assertEqual(song.best_score_value(5), 100)
        self.assertEqual(song.best_score_value(9), 890)
        self.assertEqual(song.best_score_value(78), None)

    def test_find_or_create(self):
        """ Test find or create a song """

        self.assertEqual(self.session.query(models.Song).count(), 0)
        song = models.Song.find_or_create(
            title="Patate",
            subtitle="Pasteque",
            artist="Chaussure",
            session=self.session
        )
        self.assertEqual(self.session.query(models.Song).count(), 1)
        song2 = models.Song.find_or_create(
            title="Patate",
            subtitle="Pasteque",
            artist="Chaussure",
            session=self.session
        )
        self.assertEqual(self.session.query(models.Song).count(), 1)
        self.assertEqual(song, song2)
