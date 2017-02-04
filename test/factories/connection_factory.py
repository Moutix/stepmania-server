""" Connection factory """

import factory

from smserver import models
from test.factories import base

class ConnectionFactory(base.BaseFactory):
    """ Classic connection """

    class Meta(base.BaseMeta):
        model = models.Connection

    token = factory.Faker("uuid4")
    ip = factory.Faker("ipv4")
    port = factory.Faker("pyint")
