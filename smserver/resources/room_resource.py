""" Room resources """

import hashlib

import sqlalchemy

from smserver import ability
from smserver import exceptions
from smserver import models
from smserver.resources import base

class RoomResource(base.BaseResource):
    """ Room class resource """

    def create(self, name, password=None, description=None, motd=None, type_=1):
        """ Create a new room """

        if not self.connection.can(ability.Permissions.create_room):
            raise exceptions.Unauthorized(self.token, "Create room %s" % name)

        if password:
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        room = models.Room(
            name=name,
            description=description,
            type=type_,
            password=password,
            motd=motd,
            status=1
        )
        try:
            self.session.add(room)
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            self.session.rollback()
            raise exceptions.ValidationError(self.token, "Room already exist")

        self.log.info("%s create room %s", self.token, room.id)

        for user in self.connection.active_users:
            user.set_level(room.id, 10)

        return room

    def delete(self):
        """ Delete the room """
        pass

    def list(self):
        """ List all the room """
        pass

    def get(self):
        """ Get the details of a room """
        pass

    def enter(self, room_id):
        """ Enter in a room """

        old_room = self.connection.room
        if old_room:
            self.serv.del_from_room(self.token, old_room.id)
            self.log.info("%s leave the room %s", self.token, old_room.id)

        self.connection.room_id = room_id
        self.connection.song = None

        for user in self.connection.active_users:
            if user.room_id == room_id:
                continue

            user.room_id = room_id
            if not user.room_privilege(room_id):
                user.set_level(room_id, 1)

        self.log.info("%s enter in room %s", self.token, room_id)

        self.serv.add_to_room(self.token, room_id)

    def leave(self):
        """ Leave a room """

        room = self.connection.room
        if not room:
            return

        self.serv.del_from_room(self.token, room.id)
        self.connection.song = None
        self.connection.room = None

        for user in self.connection.active_users:
            user.room = None

        self.log.info("%s leave the room %s", self.token, room.id)

        return room
