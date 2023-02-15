from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    posts = db.relationship('Blog', backref='user', passive_deletes=True)
   

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic=db.Column(db.String(20),nullable=False)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    image=db.Column(db.String(2050))
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
   


class Follow(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    followers=db.Column(db.String(100),db.ForeignKey('user.username'))
    following=db.Column(db.String(100),db.ForeignKey('user.username'))

