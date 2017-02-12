""" Room factory """

import factory

from smserver import models
from test.factories import base

class RoomFactory(base.BaseFactory):
    """ Classic empty room """

    class Meta(base.BaseMeta):
        model = models.Room

    name = factory.Sequence(lambda n: "Room %s" %n)
    motd = factory.Faker('text')
    description = factory.Faker('sentence')

    @classmethod
    def _after_postgeneration(cls, obj, _create, _results):
        obj._nb_players = None #pylint: disable=protected-access


