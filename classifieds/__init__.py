import ast
import datetime
import urllib2

from flask import Flask, session, request, current_app
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
app.config.from_object('app_settings')
db = SQLAlchemy(app)

from raven.contrib.flask import Sentry
sentry = Sentry(app, dsn=app.config['SENTRY_URL'])


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(30), db.ForeignKey('contacts.username'))
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
    username = db.Column(db.String(30), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, first, last, email, phone):
        self.username = username
        self.first_name = first
        self.last_name = last
        self.email = email
        self.phone_number = phone
        self.isAdmin = False

    def __repr__(self):
        return "<Contact %s>" % self.username


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryForHtml = db.Column(db.String(50), nullable=False)
    categoryForHumans = db.Column(db.String(50), nullable=False)

    def __init__(self, category_html, category_human):
        self.categoryForHtml = category_html
        self.categoryForHumans = category_human

    def __repr__(self):
        return "<Category '%s'>" % self.categoryForHumans


class PostCategories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postId = db.Column(db.Integer, db.ForeignKey('posts.id'))
    categoryId = db.Column(db.Integer, db.ForeignKey('categories.id'))

    def __init__(self, post_id, category_id):
        self.postId = post_id
        self.categoryId = category_id


# This import needs to be after app and db's creation, as they get imported into views.py, from which this imports.
from classifieds.views import View
View.register(app)


@app.before_request
def before_request():
    try:
        init_user()
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


from classifieds_controller import contact_is_admin


def is_user_admin():
    return contact_is_admin(session['username'])


app.jinja_env.globals.update(is_user_admin=is_user_admin)
