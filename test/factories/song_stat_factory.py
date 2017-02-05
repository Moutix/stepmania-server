""" SongStat factory """

import factory

from smserver import models
from test.factories import base
from test.factories.user_factory import UserFactory

class SongStatFactory(base.BaseFactory):
    """ Classic SongStat Song  """

    class Meta:
        model = models.SongStat

    user = factory.SubFactory(UserFactory)

    hit_mine   = 0
    avoid_mine = 0
    miss       = 0
    bad        = 0
    good       = 0
    great      = 0
    perfect    = 0
    flawless   = 0
    not_held   = 0
    held       = 0

    max_combo  = 0
    options    = ""
    score      = 0
    grade      = 0
    difficulty = 0
    feet       = 0

class SongFinishFactory(SongStatFactory):
    """ SongStat with random value"""

    hit_mine   = 5
    avoid_mine = 3
    miss       = 4
    bad        = 6
    good       = 78
    great      = 56
    perfect    = 34
    flawless   = 89
    not_held   = 4
    held       = 3

    max_combo  = 24
    options    = ""
    score      = 890000
    grade      = 2
    difficulty = 3
    feet       = 9

    duration   = 121
