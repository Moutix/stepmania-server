""" User factory """

import factory

from smserver import models
from test.factories import base
from test.factories.room_factory import RoomFactory

class UserFactory(base.BaseFactory):
    """ Classic user name """

    class Meta(base.BaseMeta):
        model = models.User

    name = factory.Sequence(lambda n: "User %s" % (n+1))
    rank = 1

    client_version = "123"
    client_name = "Socka"

    @classmethod
    def _after_postgeneration(cls, obj, _create, _results):
        obj._room_level = {} #pylint: disable=protected-access


class AdminFactory(UserFactory):
    """ Create an Admin user """
    rank = 10


class PrivilegeFactory(base.BaseFactory):
    """ Classic user name """

    class Meta(base.BaseMeta):
        model = models.Privilege

    level = 1
    room = factory.SubFactory(RoomFactory)
    user = factory.SubFactory(UserFactory)


class UserWithRoomFactory(UserFactory):
    """ User with a new room """
    room = factory.SubFactory(RoomFactory)


def user_with_room_privilege(level=1, **kwargs):
    """ Return a User with privileges for a room """
    user = UserWithRoomFactory(**kwargs)

    PrivilegeFactory(user=user, room=user.room, level=level)
    return user
