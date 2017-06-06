# Standard library imports
import datetime

# Local application imports
from app import db


class Posts(db.Model):
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(30), db.ForeignKey('contacts.username'))
    date_added = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    expired = db.Column(db.Boolean, nullable=False)

    # Relationships
    # Delete every post by a user if that user is removed from the DB
    # contact = db.relationship('contacts',
    #                           backref=db.backref('posts', cascade='all, delete-orphan'),
    #                           lazy='joined')

    def __init__(self, title, desc, price, username):
        self.title = title
        self.description = desc
        self.price = price
        self.username = username
        self.date_added = datetime.datetime.now()
        self.completed = False
        self.expired = False

    def __repr__(self):
        return '<Post #%(0)s: %(1)s>' % {'0': self.id, '1': self.title}


class Contacts(db.Model):
    # Columns
    username = db.Column(db.String(30), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, first, last, email, phone):
        self.username = username
        self.first_name = first
        self.last_name = last
        self.email = email
        self.phone_number = phone
        self.is_admin = False

    def __repr__(self):
        return "<Contact '%s'>" % self.first_name + ' ' + self.last_name


class Categories(db.Model):
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    category_for_html = db.Column(db.String(50), nullable=False)
    category_for_humans = db.Column(db.String(50), nullable=False)

    # Relationships
    # After each category gets deleted, the associated post_category rows need to be removed too.
    # The trick is, if that's the only category for the post, then it has to be changed to 'General' category,
    # so that can't be done with cascade deletion in the database. :(

    def __init__(self, category_html, category_human):
        self.category_for_html = category_html
        self.category_for_humans = category_human

    def __repr__(self):
        return "<Category '%s'>" % self.category_for_humans


class PostCategories(db.Model):
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    # Relationships
    # Delete all post_category rows if their associated post gets deleted
    # post = db.relationship('posts',
    #                        backref=db.backref('post_categories', cascade='all, delete-orphan'),
    #                        lazy='joined')

    def __init__(self, new_post_id, new_category_id):
        self.post_id = new_post_id
        self.category_id = new_category_id

    def __repr__(self):
        return '<Post #%(0)s => Category #%(1)s>' % {'0': self.post_id, '1': self.category_id}
