#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver import models, authplugin

class AuthDatabase(authplugin.AuthPlugin):
    def login(self, name, password):
        with self.server.db.session_scope() as session:
            user = (session
                    .query(models.User)
                    .filter_by(name=name)
                    .filter_by(password=password)
                    .first()
                   )

        if user:
            return True

        if not self.autocreate:
            return False

        if session.query(models.User).filter_by(name=name).first():
            return False

        with self.server.db.session_scope() as session:
            session.add(models.User(name=name, password=password))
        return True

