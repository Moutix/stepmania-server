#!/usr/bin/env python3
# -*- coding: utf8 -*-

import authplugin
import schema

class AuthDatabase(authplugin.AuthPlugin):
    def login(self, user, password):
        session = self.server.db.session()

        user = (session
                .query(schema.User)
                .filter_by(name=user)
                .filter_by(password=password)
                .first()
                )

        if user:
            return True

        if not self.autocreate:
            return False

        session.add(schema.User(name=user, password=password))
        session.commit()
        return True

