""" Start up module.

Use this module to setup the stepmania environment
"""

from smserver import conf
from smserver import sdnotify
from smserver import logger
from smserver import database
from smserver import messaging
from smserver import redis_database


def start_up(*args):
    """ Initalize all the stepmania environment """

    config = conf.load_config(*args)

    sd_notify = sdnotify.get_notifier()

    log = logger.set_logger_options(config.logger)

    log.debug("Init database")
    sd_notify.status("Init database")

    db = database.setup_db(
        type_=config.database.get("type", 'sqlite'),
        database=config.database.get("database"),
        user=config.database.get("user"),
        password=config.database.get("password"),
        host=config.database.get("host"),
        port=config.database.get("port"),
        driver=config.database.get("driver"),
    )

    if config.database["update_schema"]:
        log.info("DROP all the database tables")
        db.recreate_tables()
    else:
        db.create_tables()

    redis_url = config.get("redis", {}).get("url")
    if redis_url:
        try:
            redis_database.setup_db(redis_url)
        except ConnectionError:
            pass

    if redis_database.is_available():
        messaging.set_handler(
            messaging.RedisHandler()
        )
    else:
        messaging.set_handler(
            messaging.PythonHandler()
        )
