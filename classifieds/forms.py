__author__ = 'phg49389'

import datetime

from db_utilities import *
from models import *
from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SelectField, SubmitField, validators


# TODO: truncate description in homepage to only display ~80 chars (maybe http://jedfoster.com/Readmore.js/ ?)
# TODO: have the homepage have an option to display more of the truncated description on the homepage (expand)

# TODO: integrate some kind of sign-in process that can be used with the views (such as submitting a classified or editing info)


def get_classified_form():
    return ClassifiedForm()


def get_contact_form():
    return ContactForm()


def get_homepage():
    entries = search_classifieds(max_results=50)
    toSend = []
    for entry in entries:
        if still_active(entry.dateAdded, entry.duration):
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username]]
    return toSend


def get_contact(username):
    toReturn = Contacts.query.filter(Contacts.username.like(username)).first()
    return [toReturn.first_name, toReturn.last_name, toReturn.username, toReturn.email, toReturn.phone_number]


def view_classified(id):
    toReturn = Classifieds.query.filter(Classifieds.id.like(id)).first()
    return [toReturn.id, toReturn.title, toReturn.description, toReturn.price, toReturn.duration, toReturn.categories, toReturn.username, toReturn.dateAdded, toReturn.completed]


def filter_posts(username, selector):
    toSend = []
    if selector == "all":
        active_entries = search_classifieds(username=username)
        inactive_entries = search_classifieds(username=username, completed=True)
        for entry in active_entries:
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, True]]
        for entry in inactive_entries:
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, False]]
        toSend = sorted(toSend, key=lambda entry: entry[0])
    elif selector == "active":
        entries = search_classifieds(username=username)
        for entry in entries:
            if still_active(entry.dateAdded, entry.duration):
                toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, True]]
    elif selector == "completed":
        entries = search_classifieds(username=username, completed=True)
        for entry in entries:
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, True]]
    elif selector == "expired":
        entries = search_classifieds(username=username)
        active_entries = search_classifieds(username=username)
        inactive_entries = search_classifieds(username=username, completed=True)
        for entry in active_entries:
            if not still_active(entry.dateAdded, entry.duration):
                toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, False]]
        for entry in inactive_entries:
            if not still_active(entry.dateAdded, entry.duration):
                toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, False]]
        toSend = sorted(toSend, key=lambda entry: entry[0])
        # for entry in entries:
        #     if not still_active(entry.dateAdded, entry.duration):
        #         toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed]]
    return toSend


def query_database(params):
    entries = search_classifieds(**params)
    toSend = []
    for entry in entries:
        if still_active(entry.dateAdded, entry.duration):
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username]]
    return toSend


def still_active(date_added, duration):
    if isinstance(date_added, str):
        date_added = datetime.datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S.%f')
    num_days = 0
    if duration == "one-day":
        num_days = 1
    elif duration == "one-week":
        num_days = 7
    elif duration == "two-weeks":
        num_days = 14
    elif duration == "one-month":
        num_days = 28

    now = datetime.datetime.now()
    difference = (now - date_added).days
    return difference <= num_days


class ClassifiedForm(Form):
    title = StringField('Title:', [validators.required()])
    description = TextAreaField('Description:', [validators.required()])
    price = StringField('Price:', [validators.required()])
    duration_list = [
        ("one-day", "One Day"),
        ("one-week", "One Week"),
        ("two-weeks", "Two Weeks"),
        ("one-month", "One Month")
    ]
    duration = SelectField('How long to list:', [validators.required()], choices=duration_list, default="One Day")
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
    categories = SelectMultipleField('Categories:', [validators.required()], choices=category_list)
    submit = SubmitField("Submit")


class ContactForm(Form):
    first_name = StringField('First Name:', [validators.required()])
    last_name = StringField('Last Name:', [validators.required()])
    username = StringField('Username:', [validators.required()])
    email = StringField('Email address:', [validators.required()])
    phone_number = StringField('Phone Number:', [validators.required()])
    submit = SubmitField("Submit")


# Returns whether or not it was successfully submitted
def submit_classified_form(form_contents, username):
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
    return add_classified(storage['title'], storage['description'], storage['price'], storage['duration'], storage['categories'], username)


def submit_contact_form(form_contents):
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
    return add_contact(storage['username'], storage['first_name'], storage['last_name'], storage['email'], storage['phone_number'])
