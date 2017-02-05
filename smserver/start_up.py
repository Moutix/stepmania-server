""" Start up module.

Use this module to setup the stepmania environment
"""

from smserver import conf
from smserver import sdnotify
from smserver import logger
from smserver import database


def start_up(config):
    """ Initalize all the stepmania environment """

    if not config:
        config = conf.Conf()

    sd_notify = sdnotify.get_notifier()

    log = logger.set_logger_options(config.logger)

    log.debug("Init database")
    sd_notify.status("Init database")

    db = database.setup_db(
        type=config.database.get("type", 'sqlite'),
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
