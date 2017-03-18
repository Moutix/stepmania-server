""" Commont test file """

from smserver import start_up
from smserver import database

start_up.start_up("-c", "test/conf.yml")

db = database.get_current_db()
db.recreate_tables()
