""" Base module for all factories """

import factory
import factory.alchemy

from test import common

class BaseMeta:
    """ Parent meta class for all factories"""
    model = None
    sqlalchemy_session = common.db.session


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """ Classic Song  """

    class Meta(BaseMeta):
        pass

    id = factory.Sequence(lambda n: n+1)
