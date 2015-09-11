__author__ = 'phg49389'

import dataset
import datetime

from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SelectField, SubmitField, validators

sqlite_file = '../classifieds.db'


# Table columns are as follows:
# PRIMARY INT | TEXT  | TEXT        | TEXT  | TEXT       | TEXT     | DATETIME   | BOOLEAN
# ID          | Title | Description | Price | Categories | Username | Date Added | Completed

# ID will auto-increment on the entry being added, Title, Desc, Price, and Categories will be extracted from the form,
# Username will be metadata from the user's login to the classifieds, Date Added will be calculated on submission,
# and Completed will default to False, and the user or a moderator can mark it as Completed at a later date when it's
# either sold, or no longer for sale, or it's just been active for too long.

def create_table():
    db = dataset.connect('sqlite:///classifieds.db')
    table = db['classifieds']
    table.insert(dict(id=0, title="Creation Entry", description="This entry is simply here to "
                                                                "set the format for future entries",
                      price="$0", categories="", username="", dateAdded=datetime.datetime.now(), completed=False))


def add_entry(title, description, price, categories, username):
    table = dataset.connect('sqlite:///classifieds.db')['classifieds']
    table.insert(dict(title=title, description=description, price=price, categories=categories, username=username,
                      dateAdded=datetime.datetime.now(), completed=False))


def mark_entry_as_complete(entry_id):
    # TODO: authenticate this as either the poster or a moderator
    table = dataset.connect('sqlite:///classifieds.db')['classifieds']
    table.update(dict(id=entry_id, completed=True), ['id'])


# Returns the WTForm version of the form to be made into HTML
def get_form():
    return ClassifiedForm()


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
        ("books", "Books (no textbooks)"),
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


# Returns whether or not it was successfully submitted
def submit_form(form_contents):
    print form_contents
    print form_contents.getlist('categories')
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
    print storage
    # Add that object to the database and store the result
    # TODO: once the DB is working, make sure that this method can add an entry
    result = False
    if result:
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
