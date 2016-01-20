__author__ = 'phg49389'

import re
from db_utilities import *
from classifieds import Classifieds, Contacts
from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SubmitField, validators, ValidationError


# TODO: make it all look pretty

# TODO: implement crontab expire job
# This will run at 12:01am every night and call the URL to expire all the 180-day old posts
# 1 0 * * * wget https://classifieds.bethel.edu/expire

def get_homepage():
    entries = search_classifieds(expired=False, completed=False)
    toSend = []
    for entry in entries:
        if not entry.expired:
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username]]
    return toSend


def get_contact(username):
    toReturn = Contacts.query.filter(Contacts.username.like(username)).first()
    return [toReturn.username, toReturn.first_name, toReturn.last_name, toReturn.email, toReturn.phone_number]


def view_classified(id):
    toReturn = Classifieds.query.filter(Classifieds.id.like(id)).first()
    return [toReturn.id, toReturn.title, toReturn.description, toReturn.price, toReturn.categories, toReturn.username,
            toReturn.dateAdded, toReturn.completed, toReturn.expired]


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
        to_send += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username,
                     entry.completed, entry.expired]]
    to_send = sorted(to_send, key=lambda entry: entry[0])
    return to_send


def query_database(params):
    entries = search_classifieds(**params)
    toSend = []
    for entry in entries:
        toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username]]
    return toSend


def log_out():
    # TODO
    pass


def phone_validator():
    message = 'Must have a valid phone number'

    def _phone(form, field):
        phone_pattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')
        result = phone_pattern.search(field.data)
        if result is None:
            raise ValidationError(message)

    return _phone


class ClassifiedForm(Form):
    title = StringField('Title:', [validators.DataRequired(), validators.Length(max=100)])
    description = TextAreaField('Description:', [validators.DataRequired(), validators.Length(max=1000)])
    price = StringField('Price:', [validators.DataRequired(), validators.Length(max=50)])
    category_list = [
        ("appliances", "Appliances"),
        ("baby-kids", "Baby / Kids"),
        ("books", "Books (including Textbooks)"),
        ("cds-dvds", "CDs / DVDs"),
        ("cars-trucks", "Cars / Trucks"),
        ("clothes-accessories", "Clothes and Accessories"),
        ("computer", "Computer"),
        ("electronics", "Electronics"),
        ("furniture", "Furniture"),
        ("general", "General"),
        ("housing", "Housing"),
        ("jewelry", "Jewelry"),
        ("musical-instruments", "Musical Instruments"),
        ("photo-video", "Photo / Video"),
        ("tickets", "Tickets"),
        ("tools", "Tools"),
        ("toys-games", "Toys / Games"),
        ("video-gaming", "Video Gaming")
    ]
    categories = SelectMultipleField('Categories:', [validators.DataRequired()], choices=category_list)
    submit = SubmitField("Submit")


class ContactForm(Form):
    first_name = StringField('First Name:', [validators.DataRequired(), validators.Length(max=20)])
    last_name = StringField('Last Name:', [validators.DataRequired(), validators.Length(max=30)])
    email = StringField('Email address:', [validators.DataRequired(), validators.Email()])
    phone_number = StringField('Phone Number:', [validators.DataRequired(), phone_validator()])
    submit = SubmitField("Submit")


def send_feedback_email(form_contents, username):
    msg = MIMEText(form_contents['input'])
    msg['Subject'] = "Feedback from " + username
    msg['From'] = "classifieds@bethel.edu"
    msg['To'] = "classifieds@bethel.edu"

    print msg.as_string()

    s = smtplib.SMTP('localhost')
    s.sendmail("classifieds@bethel.edu", ["classifieds@bethel.edu"], msg.as_string())
    s.quit()
