__author__ = 'phg49389'

from classifieds import db
import datetime

class Classifieds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(15), nullable=False)
    categories = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(8), db.ForeignKey('contacts.username'))
    dateAdded = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, nullable=False)

    def __init__(self, title, desc, price, duration, categories, username):
        self.title = title
        self.description = desc
        self.price = price
        self.duration = duration
        self.categories = categories
        self.username = username
        self.dateAdded = datetime.datetime.now()
        self.completed = False

    def __repr__(self):
        return "<Classified %s>" % self.id

class Contacts(db.Model):
    username = db.Column(db.String(8), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    def __init__(self, username, first, last, email, phone):
        self.username = username
        self.first_name = first
        self.last_name = last
        self.email = email
        self.phone_number = phone

    def __repr__(self):
        return "<Contact %s>" % self.username
