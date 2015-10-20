__author__ = 'phg49389'

import dataset
import datetime

from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SelectField, SubmitField, validators

# Table columns are as follows:
# PRIMARY INT | TEXT  | TEXT        | TEXT  | TEXT       | TEXT     | DATETIME   | BOOLEAN
# ID          | Title | Description | Price | Categories | Username | Date Added | Completed

# ID will auto-increment on the entry being added, Title, Desc, Price, and Categories will be extracted from the form,
# Username will be metadata from the user's login to the classifieds, Date Added will be calculated on submission,
# and Completed will default to False, and the user or a moderator can mark it as Completed at a later date when it's
# either sold, or no longer for sale, or it's just been active for too long.


def create_classifieds_table():
    db = dataset.connect('sqlite:///classifieds.db')
    db.create_table("classifieds")
    table = db['classifieds']
    table.insert(dict(id=0, title="Creation Entry", description="This entry is simply here to "
                                                                "set the format for future entries",
                      price="$0", duration="one-week", categories="", username="", dateAdded=datetime.datetime.now(), completed=False))


def create_contacts_table():
    db = dataset.connect('sqlite:///classifieds.db')
    db.create_table("contacts")
    table = db['contacts']
    table.insert(dict(id=0, username="enttes", first_name="Test", last_name="Entry", email="enttes@bethel.edu",
                      phone_number="555-1234"))


def reset_tables():
    db = dataset.connect('sqlite:///classifieds.db')
    table = db['classifieds']
    table.drop()
    table = db['contacts']
    table.drop()
    db.create_table("classifieds")
    table = db['classifieds']
    table.insert(dict(id=0, title="Creation Entry", description="This entry is simply here to "
                                                                "set the format for future entries",
                      price="$0", categories="", username="", dateAdded=datetime.datetime.now(), completed=False))
    db.create_table("contacts")
    table = db['contacts']
    table.insert(dict(id=0, username="enttes", first_name="Test", last_name="Entry", email="enttes@bethel.edu",
                      phone_number="555-1234"))


def table_exists(desired_table_name):
    db = dataset.connect('sqlite:///classifieds.db')
    return desired_table_name in db.tables


def add_classified(title, description, price, duration, categories, username):
    table = dataset.connect('sqlite:///classifieds.db')['classifieds']
    return table.insert(
        dict(title=title, description=description, price=price, duration=duration, categories=categories, username=username,
             dateAdded=datetime.datetime.now(), completed=False))


def add_contact(username, first_name, last_name, email, phone_number):
    table = dataset.connect('sqlite:///classifieds.db')['contacts']
    return table.insert(dict(username=username, first_name=first_name, last_name=last_name, email=email,
                             phone_number=phone_number))


def mark_entry_as_complete(entry_id):
    # TODO: authenticate this as either the poster or a moderator
    table = dataset.connect('sqlite:///classifieds.db')['classifieds']
    table.update(dict(id=entry_id, completed=True), ['id'])


# Returns the WTForm version of the form to be made into HTML
def get_classified_form():
    return ClassifiedForm()


def get_contact_form():
    return ContactForm()


def get_homepage():
    table = dataset.connect('sqlite:///classifieds.db')['classifieds']
    # headers = table.columns
    entries = table.all()
    elemsToTake = table.columns  # ["username", "dateAdded", "title", "price", "categories"]
    toSend = [elemsToTake]
    for i, entry in enumerate(entries):
        if i != 0 and still_active(entry['dateAdded'], entry['duration']):
            toSend += [[entry[elem] for elem in entry if elem in elemsToTake]]
    return toSend


def view_contact(username):
    table = dataset.connect('sqlite:///classifieds.db')['contacts']
    return table.find_one(username=username)


def view_classified(id):
    table = dataset.connect('sqlite:///classifieds.db')['classifieds']
    return table.find_one(id=id)


def still_active(dateAdded, duration):
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
    difference = (now - dateAdded).days
    return difference <= duration


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
