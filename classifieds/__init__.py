import ast
import datetime
import urllib2
from flask import Flask, session, request, current_app
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


class Classifieds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
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


# This import needs to be after app and db's creation, as they get imported into views.py, from which this imports.
from classifieds.views import View
View.register(app)


@app.before_request
def before_request():
    try:
        init_user()
        app.logger.info(session['username'])
    except:
        app.logger.info("failed to init")


# This method sees who's logging in to the website, and then checks if they're in the contacts DB. If they are, it grabs
# their info from the DB for rendering. If not, then it creates a default entry for that user using info from wsapi.
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
        banner_info = urllib2.urlopen("http://wsapi.bethel.edu/username/" + username + "/names").read()
        info_dict = ast.literal_eval(banner_info)['0']
        primary_name = info_dict['firstName']
        if len(info_dict['prefFirstName']) > 0:
            primary_name = info_dict['prefFirstName']
        session['fullname'] = primary_name + " " + info_dict['lastName']
        new_contact = Contacts(username=username, first=primary_name, last=info_dict['lastName'],
                               email=username + "@bethel.edu", phone="")
        db.session.add(new_contact)
        db.session.commit()
