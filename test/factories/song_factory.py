""" Song factory """

import factory

from smserver import models

from test.factories import base

class SongFactory(base.BaseFactory):
    """ Classic Song  """

    class Meta(base.BaseMeta):
        model = models.Song

    title = factory.Faker("word")
    subtitle = factory.Faker("word")
    artist = factory.Faker("name")
