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
            raise exceptions.Forbidden(self.token, "Create room %s" % name)

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

    def delete(self, room_id):
        """ Delete the room """

        if not self.connection.can(ability.Permissions.delete_room, room_id):
            raise exceptions.Forbidden(self.token, "Delete room %s" % room_id)

        room = self.session.query(models.Room).get(room_id)

        for connection in room.connections:
            self.leave(connection)

        self.session.delete(room)
        self.session.commit()
        return True

    def list(self):
        """ List all the room available """

        if not self.connection.active_users:
            return []

        return models.Room.available_rooms(
            session=self.session,
            users=self.connection.active_users
        )

    def get(self, room_id):
        """ Get the details of a room """

        room = self.session.query(models.Room).get(room_id)
        if not room:
            raise exceptions.NotFound(self.token, "Room %s don't exist" % room_id)

        return room

    def login(self, name, password=None):
        """ Login into a room with name and password """

        room = models.Room.login(name, password, self.session)
        if not room:
            raise exceptions.Forbidden(self.token, "Invalid name or password")

        return self.enter(room)

    def enter(self, room):
        """ Enter in a room """

        if not self.connection.can(ability.Permissions.enter_room, room.id):
            raise exceptions.Forbidden(self.token, "Enter room %s" % room.id)

        if room.is_full():
            raise exceptions.Unauthorized(self.token, "Room %s is full" % room.id)

        old_room = self.connection.room
        if old_room:
            self.serv.del_from_room(self.token, old_room.id)
            self.log.info("%s leave the room %s", self.token, old_room.id)


        self.connection.room = room
        self.connection.song = None

        for user in self.connection.active_users:
            if user.room == room:
                continue

            user.room = room
            if not user.room_privilege(room.id):
                user.set_level(room.id, 1)

        self.log.info("%s enter in room %s", self.token, room.id)

        self.serv.add_to_room(self.token, room.id)

        return room

    def leave(self, connection=None):
        """ Leave a room """

        if not connection:
            connection = self.connection

        room = connection.room
        if not room:
            return

        self.serv.del_from_room(connection.token, room.id)
        connection.song = None
        connection.room = None

        for user in connection.active_users:
            user.room = None
		
        self.log.info("%s leave the room %s", self.token, room.id)
        if not room.online_users.count():
            if not room.static:
                self.server.log.info("No users deleteing Room: %s" % (room.name))
                self.session.delete(room)
                return None
        return room
