import re
from classifieds import app
from category_list import category_list

from classifieds_controller import *
from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SubmitField, validators, ValidationError

# TODO: implement crontab expire job
# This will run at 12:01am every night and call the URL to expire all the 180-day old posts
# 1 0 * * * wget https://classifieds.bethel.edu/expire

# Feature suggestion: upload images for a post?


# This method gets all the active posts, sorts them from most recent to least recent, then returns them as a list to be
# rendered
def get_homepage():
    entries = search_classifieds(expired=False, completed=False)
    toSend = []
    for entry in entries:
        if not entry[0].expired:
            toSend += [[entry[0].id, entry[0].title, entry[0].description, entry[0].price, entry[0].dateAdded,
                        entry[0].username, entry[1] + " " + entry[2], entry[0].completed, entry[0].expired]]
    return toSend


# This method takes the unique identifier of an ad in the DB, then returns it and all its details so that the rendering
# can be done intelligently (e.g., if the poster is viewing it, if it's expired or completed, etc.)
def view_classified(id):
    toReturn = Classifieds.query.filter(Classifieds.id.like(id)).first()
    contact = Contacts.query.filter(Contacts.username.like(toReturn.username)).first()
    return [toReturn.id, toReturn.title, toReturn.description, toReturn.price, toReturn.categories,
            contact.username, contact.first_name + " " + contact.last_name, toReturn.dateAdded, toReturn.completed, toReturn.expired]


# This method is used for when a poster is looking at all the ads that they've posted, and allows them to sort by the
# status of the post, whether it's active, completed, expired, or all statuses
def filter_posts(username, selector):
    to_send = []
    entries = []
    if selector == "all":
        entries = search_classifieds(username=username)
    elif selector == "active":
        entries = search_classifieds(username=username, completed=False, expired=False)
    elif selector == "completed":
        entries = search_classifieds(username=username, completed=True)
    elif selector == "expired":
        entries = search_classifieds(username=username, completed=False, expired=True)

    for entry in entries:
        to_send += [[entry[0].id, entry[0].title, entry[0].description, entry[0].price, entry[0].dateAdded,
                     entry[1] + " " + entry[2], entry[0].completed, entry[0].expired]]
    to_send = sorted(to_send, key=lambda entry: entry[0])
    return to_send


# A nice, generalized query method. Given a dictionary of kwargs, it will search through the existing DB for matching
# terms. If no term is given for a certain column, it will search for the wildcard '%'. All other search terms will be
# searched in a way so that it will do partial matches as well as full matches.
def query_database(params):
    entries = search_classifieds(**params)
    toSend = []
    for entry in entries:
        toSend += [[entry[0].id, entry[0].title, entry[0].description, entry[0].price, entry[0].dateAdded,
                    entry[0].username, entry[1] + " " + entry[2]]]
    return toSend


# This is a custom validator that I made to make sure that they put in valid phone numbers into their Contact form
def phone_validator():
    message = 'Must have a valid phone number'

    def _phone(form, field):
        phone_pattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')
        result = phone_pattern.search(field.data)
        if result is None:
            raise ValidationError(message)

    return _phone


# 2 WTForm objects that are used in rendering. Each Field in this object corresponds to the user-input columns in the DB
class ClassifiedForm(Form):
    title = StringField('Title:', [validators.DataRequired(), validators.Length(max=100)])
    description = TextAreaField('Description:', [validators.DataRequired(), validators.Length(max=1000)])
    price = StringField('Price:', [validators.DataRequired(), validators.Length(max=50)])
    categories = SelectMultipleField('Categories:', [validators.DataRequired()], choices=category_list)
    submit = SubmitField("Submit")


class ContactForm(Form):
    first_name = StringField('First Name:', [validators.DataRequired(), validators.Length(max=20)])
    last_name = StringField('Last Name:', [validators.DataRequired(), validators.Length(max=30)])
    email = StringField('Email address:', [validators.DataRequired(), validators.Email()])
    phone_number = StringField('Phone Number:', [validators.DataRequired(), phone_validator()])
    submit = SubmitField("Submit")


# A temporary method for the early stages of the new website so that users have a convenient way to provide feedback
def send_feedback_email(form_contents, username):
    msg = MIMEText(form_contents['input'])
    msg['Subject'] = "Feedback regarding classifieds.xp.bethel.edu from " + username
    msg['From'] = username + "@bethel.edu"
    msg['To'] = app.config['ADMINS']

    s = smtplib.SMTP('localhost')
    s.sendmail(username + "@bethel.edu", app.config['ADMINS'], msg.as_string())
    s.quit()
