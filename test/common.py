""" Commont test file """

from smserver import start_up
from smserver import database


start_up.start_up()

db = database.setup_db()
db.recreate_tables()
