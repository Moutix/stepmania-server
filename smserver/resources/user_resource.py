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
            raise exceptions.Forbidden(self.login, "Invalid name or password")

        password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        user = (self.session
                .query(models.User)
                .filter_by(name=name, password=password)
                .one_or_none())

        if not user:
            raise exceptions.Forbidden(self.login, "Invalid name or password")
        return user

    def login_or_create(self, name, password):
        """ Login or create a user if the name don't exists """

        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise exceptions.Forbidden(self.login, "Invalid name or password")

        user = (self.session
                .query(models.User)
                .filter_by(name=name)
                .one_or_none())

        if not user:
            return self.create(name, password)

        password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        if user.password != password:
            raise exceptions.Forbidden(self.login, "Invalid name or password")

        return user
