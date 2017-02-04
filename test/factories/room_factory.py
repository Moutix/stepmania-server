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
