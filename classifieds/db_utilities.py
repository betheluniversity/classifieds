__author__ = 'phg49389'

import datetime
from classifieds import db
from sqlalchemy import or_
from models import Classifieds, Contacts


def add_classified(title, description, price, duration, categories, username="enttes"):
    new_classified = Classifieds(title=title, desc=description, price=price, duration=duration,
                                 categories=categories, username=username)
    db.session.add(new_classified)
    db.session.commit()
    return True


def add_contact(username, first_name, last_name, email, phone_number):
    # If the username is already in here, it should update the rest of the info.
    existing_info = Contacts.query.filter(Contacts.username.like(username)).first()
    if existing_info is not None:
        existing_info.first_name = first_name
        existing_info.last_name = last_name
        existing_info.email = email
        existing_info.phone_number = phone_number
        return True
    else:
        new_contact = Contacts(username=username, first=first_name, last=last_name, email=email,
                               phone=phone_number)
        db.session.add(new_contact)
    db.session.commit()
    return True


def mark_entry_as_complete(entry_id):
    entry_to_update = Classifieds.query.filter(Classifieds.id.like(entry_id)).first()
    entry_to_update.completed = True
    db.session.commit()


def mark_entry_as_active(entry_id):
    entry_to_update = Classifieds.query.filter(Classifieds.id.like(entry_id)).first()
    entry_to_update.dateAdded = datetime.datetime.now()
    db.session.commit()


def search_classifieds(title=u"%", description=u"%", categories=u"%", username=u"%", completed=False, max_results=50):
    if isinstance(categories, list):
        or_categories = Classifieds.categories.like(u'%' + categories[0] + u'%')
        for category in categories[1:]:
            or_categories = or_(or_categories, Classifieds.categories.like(u'%' + category + u'%'))
        return Classifieds.query.filter(
                Classifieds.title.like(title), Classifieds.description.like(description),
                or_categories, Classifieds.username.like(username),
                Classifieds.completed == completed
        ).limit(max_results).all()

    return Classifieds.query.filter(
            Classifieds.title.like(title), Classifieds.description.like(description),
            Classifieds.categories.like(categories), Classifieds.username.like(username),
            Classifieds.completed == completed
    ).limit(max_results).all()
