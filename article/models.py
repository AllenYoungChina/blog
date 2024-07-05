from app import db


class Article(db.Model):
    __table__ = db.metadata.tables['article']
