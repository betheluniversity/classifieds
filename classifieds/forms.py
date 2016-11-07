import re

from classifieds import app
from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SubmitField, validators, ValidationError

from classifieds_controller import *


# This method gets all the active posts, sorts them from most recent to least recent, then returns them as a list to be
# rendered
def get_homepage():
    entries = search_posts(expired=False, completed=False)
    to_send = []
    for entry in entries:
        if not entry[0].expired:
            entry_dictionary = {
                'id': entry[0].id,
                'title': entry[0].title,
                'description': entry[0].description,
                'price': entry[0].price,
                'dateAdded': entry[0].dateAdded,
                'username': entry[0].username,
                'fullName': entry[1] + " " + entry[2],
                'completed': entry[0].completed,
                'expired': entry[0].expired
            }
            to_send.append(entry_dictionary)
    return to_send


# This method takes the unique identifier of an ad in the DB, then returns it and all its details so that the rendering
# can be done intelligently (e.g., if the poster is viewing it, if it's expired or completed, etc.)
def view_post(id):
    post = Posts.query.filter(Posts.id.like(id)).first()
    contact = Contacts.query.filter(Contacts.username.like(post.username)).first()

    to_return = {
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'price': post.price,
        'dateAdded': post.dateAdded,
        'username': post.username,
        'fullName': contact.first_name + " " + contact.last_name,
        'completed': post.completed,
        'expired': post.expired
    }

    return to_return


# This method is used for when a poster is looking at all the ads that they've posted, and allows them to sort by the
# status of the post, whether it's active, completed, expired, or all statuses
def filter_posts(username, selector):
    to_send = []
    entries = []
    if selector == "all":
        entries = search_posts(username=username)
    elif selector == "active":
        entries = search_posts(username=username, completed=False, expired=False)
    elif selector == "completed":
        entries = search_posts(username=username, completed=True)
    elif selector == "expired":
        entries = search_posts(username=username, completed=False, expired=True)
    elif selector == "external":
        entries = search_posts(username=u"%@%")

    for entry in entries:
        entry_dictionary = {
            'id': entry[0].id,
            'title': entry[0].title,
            'description': entry[0].description,
            'price': entry[0].price,
            'dateAdded': entry[0].dateAdded,
            'username': entry[0].username,
            'fullName': entry[1] + " " + entry[2],
            'completed': entry[0].completed,
            'expired': entry[0].expired
        }
        to_send.append(entry_dictionary)
    to_send = sorted(to_send, key=lambda entry: entry['id'])
    return to_send


# A nice, generalized query method. Given a dictionary of kwargs, it will search through the existing DB for matching
# terms. If no term is given for a certain column, it will search for the wildcard '%'. All other search terms will be
# searched in a way so that it will do partial matches as well as full matches.
def query_database(params):
    entries = search_posts(**params)
    to_send = []
    for entry in entries:
        entry_dictionary = {
            'id': entry[0].id,
            'title': entry[0].title,
            'price': entry[0].price,
            'dateAdded': entry[0].dateAdded,
            'username': entry[0].username,
            'fullName': entry[1] + " " + entry[2],
            'completed': entry[0].completed,
            'expired': entry[0].expired
        }
        to_send.append(entry_dictionary)
    return to_send


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
class PostForm(Form):
    title = StringField('Title:', [validators.DataRequired(), validators.Length(max=100)])
    description = TextAreaField('Description:', [validators.DataRequired(), validators.Length(max=1000)])
    price = StringField('Price:', [validators.DataRequired(), validators.Length(max=50)])
    categories = SelectMultipleField('Categories:', [validators.DataRequired()], choices=get_category_list())
    submit = SubmitField("Submit")


class ContactForm(Form):
    first_name = StringField('First Name:', [validators.DataRequired(), validators.Length(max=20)])
    last_name = StringField('Last Name:', [validators.DataRequired(), validators.Length(max=30)])
    email = StringField('Email address:', [validators.DataRequired(), validators.Email()])
    phone_number = StringField('Phone Number:', [validators.DataRequired(), phone_validator()])
    submit = SubmitField("Update")


class CategoryForm(Form):
    category_html = StringField('HTML version of the category:', [validators.DataRequired(), validators.Length(max=50)])
    category_human = StringField('Human-friendly version of the category:', [validators.DataRequired(), validators.Length(max=50)])
    submit = SubmitField("Submit")


# A temporary method for the early stages of the new website so that users have a convenient way to provide feedback
def send_feedback_email(form_contents, username):
    msg = MIMEText(form_contents['input'])
    msg['Subject'] = "Feedback regarding classifieds.bethel.edu from " + username
    msg['From'] = "classifieds@bethel.edu"
    msg['To'] = app.config['ADMINS']

    s = smtplib.SMTP('localhost')
    s.sendmail(username + "@bethel.edu", app.config['ADMINS'], msg.as_string())
    s.quit()
