#!/usr/bin/env python3
# -*- coding: utf8 -*-

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smserver.models import schema

class DataBase(object):
    def __init__(self, type="sqlite", database=None, user=None,
                 password=None, host=None, port=None, driver=None):
        self._type = type
        if not type:
            self._type = "sqlite"
        self._database = database
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._driver = driver
        self._engine = None

    @property
    def engine(self):
        if self._engine:
            return self._engine

        self._engine = create_engine(self._database_url)
        return self.engine

    @property
    def session(self):
        return sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def _database_url(self):
        return '{dialect}{driver}://{username}{password}{host}{port}{database}'.format(
            dialect=self._type,
            driver="+%s" % self._driver if self._driver else "",
            username=self._user if self._user else "",
            password=":%s" % self._password if self._password else "",
            host="@%s" % self._host if self._host else "",
            port=":%s" % self._port if self._port else "",
            database="/%s" % self._database if self._database else ""
        )

    def create_tables(self):
        schema.Base.metadata.create_all(self.engine)

    def recreate_tables(self):
        schema.Base.metadata.drop_all(self.engine)
        schema.Base.metadata.create_all(self.engine)

    @classmethod
    def test_db(cls):
        db = cls()
        db.create_tables()
        return db

