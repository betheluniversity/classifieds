__author__ = 'phg49389'

import datetime

from classifieds import db
from db_utilities import *
from models import *
from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SelectField, SubmitField, validators

# Table columns are as follows:
# PRIMARY INT | TEXT  | TEXT        | TEXT  | TEXT       | TEXT     | DATETIME   | BOOLEAN
# ID          | Title | Description | Price | Categories | Username | Date Added | Completed

# ID will auto-increment on the entry being added, Title, Desc, Price, and Categories will be extracted from the form,
# Username will be metadata from the user's login to the classifieds, Date Added will be calculated on submission,
# and Completed will default to False, and the user or a moderator can mark it as Completed at a later date when it's
# either sold, or no longer for sale, or it's just been active for too long.

# TODO: truncate description in homepage to only display ~80 chars
# TODO: have the homepage have an option to display more of the truncated description on the homepage (expand)

# TODO: integrate some kind of sign-in process that can be used with the views (such as submitting a classified or editing info)

# TODO: expand the multiple-select box height in "submit a new classified" form

# TODO: write script that runs every midnight to mark classifieds as expired


def get_classified_form():
    return ClassifiedForm()


def get_contact_form():
    return ContactForm()


def get_homepage():
    # TODO: update to new db

    entries = search_classifieds(max_results=50)
    elemsToTake = "table.columns"  # ["username", "dateAdded", "title", "price", "categories"]
    toSend = []
    for i, entry in enumerate(entries):
        if i != 0 and still_active(entry['dateAdded'], entry['duration']):
            toSend += [[entry[elem] for elem in entry if elem in elemsToTake]]
    return toSend


def view_contact(username):
    return Contacts.query(username=username).first()


def view_classified(id):
    return Classifieds.query(id=id).first()


def filter_posts(username, selector):
    # TODO: update to new db
    table = ""
    elemsToTake = table.columns  # ["username", "dateAdded", "title", "price", "categories"]
    toSend = []
    if selector == "all":
        entries = table.find(username=username)
        for entry in entries:
            toSend += [[entry[elem] for elem in entry if elem in elemsToTake]]
    elif selector == "active":
        entries = table.find(username=username, completed=False)
        for entry in entries:
            if still_active(entry['dateAdded'], entry['duration']):
                toSend += [[entry[elem] for elem in entry if elem in elemsToTake]]
    elif selector == "completed":
        entries = table.find(username=username, completed=True)
        for entry in entries:
            toSend += [[entry[elem] for elem in entry if elem in elemsToTake]]
    elif selector == "expired":
        entries = table.find(username=username, completed=False)
        for entry in entries:
            if not still_active(entry['dateAdded'], entry['duration']):
                toSend += [[entry[elem] for elem in entry if elem in elemsToTake]]
    return toSend


def query_database(params):
    paramList = ""
    for param in list(params):
        paramList += "("
        for val in params.getlist(param):
            paramList += param + " LIKE '%" + val + "%'"
            if params.getlist(param).index(val) < len(params.getlist(param)) - 1:
                paramList += " OR "
        paramList += ")"
        if list(params).index(param) < len(list(params)) - 1:
            paramList += " AND "
    entries = db.query("SELECT * FROM classifieds WHERE " + paramList)
    elemsToTake = "table.columns"  # ["username", "dateAdded", "title", "price", "categories"]
    toSend = []
    for i, entry in enumerate(entries):
        if still_active(entry['dateAdded'], entry['duration']):
            toSend += [[entry[elem] for elem in entry if elem in elemsToTake]]
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
    # TODO: once the DB is working, make sure that this method can add an entry
    result = add_classified(storage['title'], storage['description'], storage['price'], storage['duration'], storage['categories'], username)
    print result
    # TODO: move this to a template
    if result > 0:
        return """
        <html>
            <head>
                <title>Success</title>
            </head>
            <body>
                Classified successfully submitted!
            </body>
        </html>
        """
    else:
        return """
        <html>
            <head>
                <title>Failure</title>
            </head>
            <body>
                Classified was not successfully submitted.
            </body>
        </html>
        """


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
    # TODO: once the DB is working, make sure that this method can add an entry
    result = add_contact(storage['username'], storage['first_name'], storage['last_name'], storage['email'], storage['phone_number'])
    print result
    if result > 0:
        return """
        <html>
            <head>
                <title>Success</title>
            </head>
            <body>
                Contact successfully submitted!
            </body>
        </html>
        """
    else:
        return """
        <html>
            <head>
                <title>Failure</title>
            </head>
            <body>
                Contact was not successfully submitted.
            </body>
        </html>
        """
