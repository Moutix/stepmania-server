""" Ban factory """

from smserver import models
from test.factories import base

class BanFactory(base.BaseFactory):
    """ Classic user name """

    class Meta(base.BaseMeta):
        model = models.Ban

    fixed = False
