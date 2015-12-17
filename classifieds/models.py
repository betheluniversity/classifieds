__author__ = 'phg49389'

from classifieds import db
import datetime

# Table columns are as follows:
# PRIMARY INT | TEXT  | TEXT        | TEXT  | TEXT       | TEXT     | DATETIME   | BOOLEAN
# ID          | Title | Description | Price | Categories | Username | Date Added | Completed

# ID will auto-increment on the entry being added, Title, Desc, Price, and Categories will be extracted from the form,
# Username will be metadata from the user's login to the classifieds, Date Added will be calculated on submission,
# and Completed will default to False, and the user or a moderator can mark it as Completed at a later date when it's
# either sold, or no longer for sale, or it's just been active for too long.

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
        return "<Classified #%(0)s: %(1)s>" % {'0': self.id, '1': self.title}

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
