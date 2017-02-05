""" Commont test file """

from smserver import start_up
from smserver import database
from smserver import conf

start_up.start_up(conf.Conf())

db = database.setup_db()
db.recreate_tables()
