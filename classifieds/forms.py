__author__ = 'phg49389'

from flask import session
from db_utilities import *
from classifieds import Classifieds, Contacts
from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SubmitField, validators


# TODO: truncate description in homepage to only display ~80 chars (maybe http://jedfoster.com/Readmore.js/ ?)
# TODO: have the homepage have an option to display more of the truncated description on the homepage (expand)

# TODO: sanitize search queries to guard against injection attacks and make sure that the text doesn't go over the
# TODO:     allotted space in the DB object (500 chars, 10 chars, etc...)

def get_classified_form():
    return ClassifiedForm()


def get_contact_form():
    return ContactForm()


def get_homepage():
    entries = search_classifieds()
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
    toSend = []
    if selector == "all":
        active_entries = search_classifieds(username=username)
        completed_entries = search_classifieds(username=username, completed=True)
        for entry in active_entries:
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, entry.expired]]
        for entry in completed_entries:
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, entry.expired]]
        toSend = sorted(toSend, key=lambda entry: entry[0])
    elif selector == "active":
        entries = search_classifieds(username=username)
        for entry in entries:
            if not entry.expired:
                toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, entry.expired]]
    elif selector == "completed":
        entries = search_classifieds(username=username, completed=True)
        for entry in entries:
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, entry.expired]]
    elif selector == "expired":
        active_entries = search_classifieds(username=username)
        inactive_entries = search_classifieds(username=username, completed=True)
        for entry in active_entries:
            if entry.expired:
                toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, False]]
        for entry in inactive_entries:
            if entry.expired:
                toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username, entry.completed, False]]
        toSend = sorted(toSend, key=lambda entry: entry[0])
    return toSend


def query_database(params):
    entries = search_classifieds(**params)
    toSend = []
    for entry in entries:
        if not entry.expired:
            toSend += [[entry.id, entry.title, entry.description, entry.price, entry.dateAdded, entry.username]]
    return toSend


class ClassifiedForm(Form):
    title = StringField('Title:', [validators.required()])
    description = TextAreaField('Description:', [validators.required()])
    price = StringField('Price:', [validators.required()])
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
    return add_classified(storage['title'], storage['description'], storage['price'], storage['categories'], username)


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
    return add_contact(session['username'], storage['first_name'], storage['last_name'], storage['email'], storage['phone_number'])
