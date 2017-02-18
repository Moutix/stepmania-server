""" User resources """

import hashlib

import sqlalchemy

from smserver import exceptions
from smserver import models
from smserver.resources import base

class UserResource(base.BaseResource):
    """ User class resource """

    MIN_PASSWORD_LENGTH = 8

    def create(self, name, password, email=None, rank=1):
        """ Create a new user """

        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise exceptions.ValidationError(self.token, "Password too short")

        if rank > 1 and rank > self.connection.level():
            raise exceptions.Unauthorized(
                self.token,
                "Unauthorized to create user with rank %s" % rank
            )

        password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        user = models.User(
            name=name,
            password=password,
            email=email,
            rank=rank
        )
        try:
            self.session.add(user)
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            self.session.rollback()
            raise exceptions.ValidationError(self.token, "User already exist")

        self.log.info("%s create user %s", self.token, user.id)

        return user

    def login(self, name, password):
        """ Login a new user in our database """

        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise exceptions.Forbidden(self.token, "Invalid name or password")

        password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        user = (self.session
                .query(models.User)
                .filter_by(name=name, password=password)
                .one_or_none())

        if not user:
            raise exceptions.Forbidden(self.token, "Invalid name or password")

        if models.Ban.is_ban(self.session, user_id=user.id):
            raise exceptions.Forbidden(self.token, "User ban from this server")


        self.log.info("%s successfully login user %s", self.token, name)

        return user

    def login_or_create(self, name, password):
        """ Login or create a user if the name don't exists """

        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise exceptions.Forbidden(self.token, "Invalid name or password")

        user = (self.session
                .query(models.User)
                .filter_by(name=name)
                .one_or_none())

        if not user:
            return self.create(name, password)

        return self.login(name, password)

    def connect(self, user, pos=0):
        """ Connect the user in the given position """
        if user.online and user not in self.connection.users:
            raise exceptions.Unauthorized(self.token, "User already online")

        nb_onlines = models.User.nb_onlines(self.session)
        max_users = self.serv.config.server.get("max_users", -1)
        if max_users > 0 and nb_onlines >= max_users:
            raise exceptions.Unauthorized(
                self.token,
                "nb max users reaches (%s/%s)" % (nb_onlines, max_users)
            )

        for online_user in self.connection.active_users:
            if online_user.pos == pos and online_user != user:
                self.log.info("%s log out user %s", self.token, online_user.name)
                online_user.pos = None
                online_user.online = False

        user.pos = pos
        user.online = True

        user.connection = self.connection
        user.room_id = self.connection.room_id
        user.last_ip = self.connection.ip
        user.client_name = self.connection.client_name
        user.client_version = self.connection.client_version

        self.serv.send_sd_running_status(session=self.session)

        return user
