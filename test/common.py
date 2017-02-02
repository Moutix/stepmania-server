""" Commont test file """

import sqlalchemy
from smserver.models import schema

Session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker())

engine = sqlalchemy.create_engine('sqlite://')

# It's a scoped_session, and now is the time to configure it.
Session.configure(bind=engine)

schema.Base.metadata.drop_all(engine)
schema.Base.metadata.create_all(engine)
