""" Redis database module

To get the current redis use `get_current_db`
"""

import redis


class RedisDataBase(object):
    """ The RedisDtaBase hold a redis connection pool """

    def __init__(self, url="redis://localhost:6379/0"):
        self.url = url

        self.connection_pool = redis.ConnectionPool.from_url(
            url,
            decode_responses=True,
        )
        if not self.ping():
            raise ConnectionError("Redis server is unavailable")

    def ping(self):
        """ Test if the redis database is available """

        connection = self.new_connection()
        try:
            connection.ping()
        except redis.exceptions.ConnectionError:
            return False

        return True

    def new_connection(self):
        """ Get a new redis connection """
        return redis.StrictRedis(
            connection_pool=self.connection_pool,
            socket_connect_timeout=1
        )


class _RedisDatabase:
    db = None

def setup_db(url="redis://localhost:6379/0"):
    """ Initalize the redis database"""

    _RedisDatabase.db = RedisDataBase(url=url)

    return _RedisDatabase.db

def get_current_db():
    """ Get the current redis database """
    return _RedisDatabase.db

def new_connection():
    """ Return a new redis connection """
    return _RedisDatabase.db.new_connection()

def is_available():
    """ Return True if the redis server is correctly configured """
    return bool(_RedisDatabase.db)
