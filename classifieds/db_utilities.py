__author__ = 'phg49389'

from classifieds import db
from models import Classifieds, Contacts


def add_classified(title, description, price, duration, categories, username="enttes"):
    new_classified = Classifieds(title=title, desc=description, price=price, duration=duration,
                                 categories=categories, username=username)
    db.session.add(new_classified)
    db.session.commit()


def add_contact(username, first_name, last_name, email, phone_number):
    new_contact = Contacts(username=username, first=first_name, last=last_name, email=email,
                           phone=phone_number)
    db.session.add(new_contact)
    db.session.commit()


def mark_entry_as_complete(entry_id):
    entry_to_update = Classifieds.query.filter_by(id=entry_id).first()
    entry_to_update.completed = True
    db.session.update(entry_to_update)
    db.session.commit()


def search_classifieds(title="*", description="*", categories="*"):
    results = Classifieds.query.filter_by(Classifieds.title.like(title), Classifieds.description.like(description),
                                          Classifieds.categories.like(categories)).all()
    toReturn = []
    for result in results:
        toReturn += [result]
    return toReturn
