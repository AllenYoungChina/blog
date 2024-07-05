from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __table__ = db.metadata.tables['user']
