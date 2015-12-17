__author__ = 'phg49389'

from classifieds import db
from models import Classifieds, Contacts


def add_classified(title, description, price, duration, categories, username="enttes"):
    new_classified = Classifieds(title=title, desc=description, price=price, duration=duration,
                                 categories=categories, username=username)
    db.session.add(new_classified)
    db.session.commit()
    return True


def add_contact(username, first_name, last_name, email, phone_number):
    if Contacts.query.filter(Contacts.username.like(username)).first() is not None:
        return False
    new_contact = Contacts(username=username, first=first_name, last=last_name, email=email,
                           phone=phone_number)
    db.session.add(new_contact)
    db.session.commit()
    return True


def mark_entry_as_complete(entry_id):
    entry_to_update = Classifieds.query.filter(Classifieds.id.like(entry_id)).first()
    entry_to_update.completed = True
    db.session.commit()


def search_classifieds(title="%", description="%", categories="%", username="%", completed=False, max_results=50):
    return Classifieds.query.filter(
            Classifieds.title.like(title), Classifieds.description.like(description),
            Classifieds.categories.like(categories), Classifieds.username.like(username),
            Classifieds.completed == completed
    ).limit(max_results).all()
