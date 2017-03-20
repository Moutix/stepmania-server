""" Database module

To get the current database use `get_current_db`
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from smserver.models import schema


class DataBase(object):
    """
        The DataBase class hold information about a given database.

        It's a wrapper around SQLAlchemy database creation.
        By default, it create a in memory sqlite database.

        :param str type_: Type of database (sqlite, mysql, postgresql, ...)
        :param str database: Name of the database (file for sqlite)
        :param str user: User of the database
        :param str password: Password of the database
        :param str host: Location of the database (localhost for local)
        :param int port: Port of the database
        :param str driver: Driver for communication with the database.
    """

    def __init__(self, type_="sqlite", database=None, user=None,
                 password=None, host=None, port=None, driver=None):
        self._type = type_
        if not type_:
            self._type = "sqlite"
        self._database = database
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._driver = driver

        self._engine = None
        self._session = None

    @property
    def engine(self):
        """ SQLAlchemy engine assosiate with the DataBase """


        if self._engine:
            return self._engine

        self._engine = create_engine(self._database_url)
        return self._engine

    @property
    def session(self):
        """ Return a SQLAlchemy Session maker """

        if self._session:
            return self._session

        self._session = scoped_session(sessionmaker(bind=self.engine))
        return self._session

    @contextmanager
    def session_scope(self, session=None):
        """
            Provide a transactional scope around a series of operations.
        """

        close_connection = False
        if not session:
            close_connection = True
            session = self.session() #pylint: disable=not-callable

        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            if close_connection:
                session.close()

    @property
    def _database_url(self):
        """
            Return a SQLAlchemy URL to use when creating the engine

            :Example:
            >>> from smserver.database import DataBase

            >>> DataBase(database="stepmania.db")._database_url
            sqlite:///stepmania.db

            >>> DataBase(
            ...     type_="postgresql",
            ...     user="u/se//r",
            ...     password="password",
            ...     host="127.0.0.1",
            ...     database="stepmania"
            ... )._database_url
            postgresql://u%2Fse%2F%2Fr:***@127.0.0.1/stepmania

            >>> DataBase(
            ...     type_="mysql",
            ...     user="user@mail.fr",
            ...     password="password",
            ...     host="localhost",
            ...     database="stepmania",
            ...     driver="pymysql"
            ... )._database_url
            mysql+pymysql://user%40mail.fr:***@localhost/stepmania
        """

        return URL(
            '%s%s' % (self._type, "+%s" % self._driver if self._driver else ""),
            username=self._user,
            password=self._password,
            host=self._host,
            database=self._database,
            port=self._port,
        )

    def create_tables(self):
        """
            Create all the table in the DataBase if they don't exist.
        """

        schema.Base.metadata.create_all(self.engine)

    def recreate_tables(self):
        """
            Drop and recreate all the table in the DataBase
        """

        schema.Base.metadata.drop_all(self.engine)
        schema.Base.metadata.create_all(self.engine)


class _Database:
    db = None


def setup_db(type_="sqlite", database=None, user=None, password=None,
             host=None, port=None, driver=None):
    """ Initalize the database"""

    _Database.db = DataBase(
        type_=type_,
        database=database,
        user=user,
        password=password,
        host=host,
        port=port,
        driver=driver,
    )

    return _Database.db

def get_current_db():
    """ Get the current database """
    return _Database.db
