__author__ = 'phg49389'

import sqlite3

from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SelectField, SubmitField, validators

sqlite_file = '../app.db'
table_name = "classifieds"


def create_table():
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute("CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)".format(tn=table_name, nf="classified_id", ft="INTEGER"))
    columns_to_add = ["title", "description", "price", "duration", "categories"]
    for column_name in columns_to_add:
        c.execute("ALTER TABLE {tn} ADD COLUMN {cn} {ct}".format(tn=table_name, cn=column_name, ct="TEXT"))

    conn.commit()
    conn.close()


def add_entry(title, description, price, duration, categories):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute("INSERT INTO {tn} VALUES (NULL, %(0)s, %(1)s, %(2)s, %(3)s, %(4)s)".format(tn=table_name)
              % {'0': title,
                 '1': description,
                 '2': price,
                 '3': duration,
                 '4': categories})

    conn.commit()
    conn.close()


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
