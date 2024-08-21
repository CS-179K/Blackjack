# models.py

from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(300))
    name = db.Column(db.String(100))
    games=db.Column(db.Integer(), default=0)
    bank=db.Column(db.Integer(), default=0)
    high_score=db.Column(db.Integer(), default=0)
    wins=db.Column(db.Integer(), default=0)