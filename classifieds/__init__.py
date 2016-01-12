__author__ = 'phg49389'

import datetime
from flask import Flask, session, request, current_app
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

class Classifieds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    categories = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(8), db.ForeignKey('contacts.username'))
    dateAdded = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    expired = db.Column(db.Boolean, nullable=False)

    def __init__(self, title, desc, price, categories, username):
        self.title = title
        self.description = desc
        self.price = price
        self.categories = categories
        self.username = username
        self.dateAdded = datetime.datetime.now()
        self.completed = False
        self.expired = False

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


from classifieds.views import View
View.register(app)


@app.before_request
def before_request():
    try:
        init_user()
        app.logger.info(session['username'])
    except:
        app.logger.info("failed to init")


def init_user():
    if current_app.config['ENVIRON'] == 'prod':
        username = request.environ.get('REMOTE_USER')
    else:
        username = current_app.config['TEST_USER']
    session['username'] = username
    contact = Contacts.query.filter(Contacts.username.like(username)).first()
    if contact is not None:
        session['fullname'] = contact.first_name + " " + contact.last_name
    else:
        session['fullname'] = "please update your profile"

