__author__ = 'phg49389'

import re
from flask import session
from db_utilities import *
from classifieds import Classifieds, Contacts
from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SubmitField, validators, ValidationError


# TODO: truncate description in homepage to only display ~80 chars (maybe http://jedfoster.com/Readmore.js/ ?)
# TODO: have the homepage have an option to display more of the truncated description on the homepage (expand)

# TODO: write crontab job that calls "wget https://classifieds.bethel.edu/expire"

def get_classified_form():
    return ClassifiedForm()


def get_contact_form():
    return ContactForm()


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


def submit_classified_form(form_contents, username):
    form = ClassifiedForm(form_contents)
    isValid = form.validate()
    if not isValid:
        return [isValid, form.errors]
    storage = {}
    for key in form_contents:
        if key == "submit":
            continue
        raw_values = form_contents.getlist(key)
        if len(raw_values) > 1:
            parsed_values = ""
            for val in raw_values:
                parsed_values += val + ";"
            parsed_values = parsed_values[:-1]  # Remove last semicolon; unnecessary
        else:
            parsed_values = raw_values[0]
        storage[key] = parsed_values
    # Add that object to the database and store the result
    return [add_classified(storage['title'], storage['description'], storage['price'], storage['categories'], username)]


def submit_contact_form(form_contents):
    form = ContactForm(form_contents)
    isValid = form.validate()
    if not isValid:
        return [isValid, form.errors]
    storage = {}
    for key in form_contents:
        if key == "submit":
            continue
        raw_values = form_contents.getlist(key)
        if len(raw_values) > 1:
            parsed_values = ""
            for val in raw_values:
                parsed_values += val + ";"
            parsed_values = parsed_values[:-1]  # Remove last semicolon; unnecessary
        else:
            parsed_values = raw_values[0]
        storage[key] = parsed_values
    # Add that object to the database and store the result
    return [add_contact(session['username'], storage['first_name'], storage['last_name'], storage['email'], storage['phone_number'])]


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
    description = TextAreaField('Description:', [validators.DataRequired(), validators.Length(max=500)])
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

