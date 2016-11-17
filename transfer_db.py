import datetime
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

basedir = os.path.abspath(os.path.dirname(__file__))

# This script is designed to gather all of the data from the existing app.db, and then put it into the new DB form

# Step 1: access the old database

old = Flask(__name__)
old.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'old_db.db')
# old.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(basedir, 'db_repository')
old_db = SQLAlchemy(old)

# Old Models:


class Classifieds(old_db.Model):
    id = old_db.Column(old_db.Integer, primary_key=True)
    title = old_db.Column(old_db.String(100), nullable=False)
    description = old_db.Column(old_db.String(1000), nullable=False)
    price = old_db.Column(old_db.String(50), nullable=False)
    categories = old_db.Column(old_db.String(200), nullable=False)
    username = old_db.Column(old_db.String(30), old_db.ForeignKey('contacts.username'))
    dateAdded = old_db.Column(old_db.DateTime, nullable=False)
    completed = old_db.Column(old_db.Boolean, nullable=False)
    expired = old_db.Column(old_db.Boolean, nullable=False)

    def __init__(self, title, desc, price, categories, username):
        self.title = title
        self.description = desc
        self.price = price
        self.categories = categories
        self.username = username
        self.dateAdded = datetime.datetime.now()
        self.completed = False
        self.expired = False

    def __repr__(self):
        return "<Classified #%(0)s: %(1)s>" % {'0': self.id, '1': self.title}


class Contacts(old_db.Model):
    username = old_db.Column(old_db.String(30), primary_key=True)
    first_name = old_db.Column(old_db.String(20), nullable=False)
    last_name = old_db.Column(old_db.String(30), nullable=False)
    email = old_db.Column(old_db.String(50), nullable=False)
    phone_number = old_db.Column(old_db.String(15), nullable=False)
    isAdmin = old_db.Column(old_db.Boolean, nullable=False, default=False)

    def __init__(self, username, first, last, email, phone):
        self.username = username
        self.first_name = first
        self.last_name = last
        self.email = email
        self.phone_number = phone
        self.isAdmin = False

    def __repr__(self):
        return "<Contact %s>" % self.username

# Step 2: instantiate the new database

new = Flask(__name__)
new.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'new_db.db')
# new.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(basedir, 'db_repository')
new_db = SQLAlchemy(new)

# New models:


class Posts(new_db.Model):
    id = new_db.Column(new_db.Integer, primary_key=True)
    title = new_db.Column(new_db.String(100), nullable=False)
    description = new_db.Column(new_db.String(1000), nullable=False)
    price = new_db.Column(new_db.String(50), nullable=False)
    username = new_db.Column(new_db.String(30), new_db.ForeignKey('contacts.username'))
    date_added = new_db.Column(new_db.DateTime, nullable=False)
    completed = new_db.Column(new_db.Boolean, nullable=False)
    expired = new_db.Column(new_db.Boolean, nullable=False)

    def __init__(self, title, desc, price, username):
        self.title = title
        self.description = desc
        self.price = price
        self.username = username
        self.date_added = datetime.datetime.now()
        self.completed = False
        self.expired = False

    def __repr__(self):
        return "<Post #%(0)s: %(1)s>" % {'0': self.id, '1': self.title}


class NewContacts(new_db.Model):
    username = new_db.Column(new_db.String(30), primary_key=True)
    first_name = new_db.Column(new_db.String(20), nullable=False)
    last_name = new_db.Column(new_db.String(30), nullable=False)
    email = new_db.Column(new_db.String(50), nullable=False)
    phone_number = new_db.Column(new_db.String(15), nullable=False)
    is_admin = new_db.Column(new_db.Boolean, nullable=False, default=False)

    def __init__(self, username, first, last, email, phone):
        self.username = username
        self.first_name = first
        self.last_name = last
        self.email = email
        self.phone_number = phone
        self.is_admin = False

    def __repr__(self):
        return "<Contact %s>" % self.username


class Categories(new_db.Model):
    id = new_db.Column(new_db.Integer, primary_key=True)
    category_for_html = new_db.Column(new_db.String(50), nullable=False)
    category_for_humans = new_db.Column(new_db.String(50), nullable=False)

    def __init__(self, category_html, category_human):
        self.category_for_html = category_html
        self.category_for_humans = category_human

    def __repr__(self):
        return "<Category '%s'>" % self.category_for_humans


class PostCategories(new_db.Model):
    id = new_db.Column(new_db.Integer, primary_key=True)
    post_id = new_db.Column(new_db.Integer, new_db.ForeignKey('posts.id'))
    category_id = new_db.Column(new_db.Integer, new_db.ForeignKey('categories.id'))

    def __init__(self, new_post_id, new_category_id):
        self.post_id = new_post_id
        self.category_id = new_category_id

    def __repr__(self):
        return "<Post #%(0)s => Category #%(1)s>" % {'0': self.post_id, '1': self.category_id}


# Step 3: put the old data into the new database
try:
    # Part 1: transfer old contacts into new contacts
    for old_contact in Contacts.query.all():
        new_contact = NewContacts(old_contact.username,
                                  old_contact.first_name,
                                  old_contact.last_name,
                                  old_contact.email,
                                  old_contact.phone_number)
        new_contact.is_admin = old_contact.isAdmin
        new_db.session.add(new_contact)

    # Part 2: add all the categories
    category_pairs = [
        ("appliances", "Appliances"),
        ("baby-kids", "Baby/Kids Items"),
        ("cars-trucks", "Cars/Trucks"),
        ("cds-dvds", "CDs/DVDs"),
        ("clothes-accessories", "Clothes/Accessories"),
        ("computer", "Computer"),
        ("electronics", "Electronics"),
        ("furniture", "Furniture"),
        ("general", "General"),
        ("housing", "Housing"),
        ("jewelry", "Jewelry"),
        ("musical-instruments", "Musical Instruments"),
        ("photo-video", "Photo/Video"),
        ("rides", "Rides"),
        ("tickets", "Tickets"),
        ("tools", "Tools"),
        ("toys-games", "Toys/Games"),
        ("video-gaming", "Video Gaming")
    ]
    for pair in category_pairs:
        new_category = Categories(pair[0], pair[1])
        new_db.session.add(new_category)

    # Part 3: iterate through old posts, and add them to the new DB.
    for old_post in Classifieds.query.all():
        new_post = Posts(old_post.title,
                         old_post.description,
                         old_post.price,
                         old_post.username)
        new_post.date_added = old_post.dateAdded
        new_post.completed = old_post.completed
        new_post.expired = old_post.expired
        new_db.session.add(new_post)
        post_id = Posts.query.order_by(desc(Posts.id)).first().id
        # Part 4: iterate through old post's categories and add PostCategory rows accordingly
        for old_category in old_post.categories.split(";"):
            category_id = Categories.query.filter(Categories.category_for_html.like(old_category)).first().id
            new_post_category_row = PostCategories(post_id, category_id)
            new_db.session.add(new_post_category_row)

    # Step 4: commit the changes
    new_db.session.commit()
    print "Data has been successfully transferred to new_db.db"

    # Step 5: change the name of the contacts table from "new_contacts" to "contacts" using sqlite3
except Exception as e:
    new_db.session.rollback()
    print e.message
    print "Data failed to be transferred"
