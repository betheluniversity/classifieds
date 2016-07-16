import datetime
import smtplib
from email.mime.text import MIMEText

from classifieds import db, Classifieds, Contacts
from sqlalchemy import or_, desc


# In general, these methods simply enable loose coupling between the database and the server. Some take in the
# necessary arguments needed by the database that can't be generated, and return the right value, while others are more
# or less void methods that change specific entries in the database for functionality purposes.


def add_classified(title, description, price, categories, username):
    new_classified = Classifieds(title=title, desc=description, price=price, categories=categories, username=username)
    try:
        db.session.add(new_classified)
        db.session.commit()
    except:
        return False
    return True


def add_contact(username, first_name, last_name, email, phone_number):
    # If the username is already in here, it should update the rest of the info.
    try:
        existing_info = Contacts.query.filter(Contacts.username.like(username)).first()
        if existing_info is not None:
            existing_info.first_name = first_name
            existing_info.last_name = last_name
            existing_info.email = email
            existing_info.phone_number = phone_number
        else:
            new_contact = Contacts(username=username, first=first_name, last=last_name, email=email,
                                   phone=phone_number)
            db.session.add(new_contact)
        db.session.commit()
    except:
        return False
    return True


def get_contact(username):
    toReturn = Contacts.query.filter(Contacts.username.like(username)).first()
    return [toReturn.username, toReturn.first_name, toReturn.last_name, toReturn.email, toReturn.phone_number]


def mark_entry_as_complete(entry_id, username):
    entry_to_update = Classifieds.query.filter(Classifieds.id.like(entry_id)).first()
    if entry_to_update.username == username:
        entry_to_update.completed = True
        db.session.commit()


def mark_entry_as_active(entry_id, username):
    entry_to_update = Classifieds.query.filter(Classifieds.id.like(entry_id)).first()
    if entry_to_update.username == username:
        entry_to_update.dateAdded = datetime.datetime.now()
        entry_to_update.expired = False
        db.session.commit()


# If we want to change this over to pagination at a later date, I'm putting in commented code that should get you
# started on it.
def search_classifieds(title=u"%", description=u"%", categories=u"%", username=u"%", completed=u"%", expired=u"%"):
    # def search_classifieds(title=u"%", description=u"%", categories=u"%", username=u"%", completed=u"%", expired=u"%",
    #                        max_results=50, page_no=1):
    if isinstance(title, list):
        titles = Classifieds.title.like(u'%' + title[0] + u'%')
        for term in title[1:]:
            titles = or_(titles, Classifieds.title.like(u'%' + term + u'%'))
    else:
        titles = Classifieds.title.like(title)

    if isinstance(description, list):
        descriptions = Classifieds.description.like(u'%' + description[0] + u'%')
        for term in description[1:]:
            descriptions = or_(descriptions, Classifieds.description.like(u'%' + term + u'%'))
    else:
        descriptions = Classifieds.description.like(description)

    if isinstance(categories, list):
        or_categories = Classifieds.categories.like(u'%' + categories[0] + u'%')
        for term in categories[1:]:
            or_categories = or_(or_categories, Classifieds.categories.like(u'%' + term + u'%'))
    else:
        or_categories = Classifieds.categories.like(categories)

    if completed == u"%":
        completed = Classifieds.completed.like(completed)
    elif isinstance(completed, bool):
        completed = Classifieds.completed == completed

    if expired == u"%":
        expired = Classifieds.expired.like(expired)
    elif isinstance(expired, bool):
        expired = Classifieds.expired == expired

    return Classifieds.query.join(Contacts, Contacts.username == Classifieds.username).add_columns(Contacts.first_name,
        Contacts.last_name).order_by(desc(Classifieds.dateAdded)).filter(
            titles, descriptions, or_categories, Classifieds.username.like(username),
            completed, expired
    ).all()
    # ).limit(max_results).offset(max_results * (page_no - 1)).all()


def expire_old_posts():
    all_entries = search_classifieds(completed=False, expired=False)
    for entry in all_entries:
        now = datetime.datetime.now().date()
        then = entry.dateAdded.date()
        if (now - then).days >= 180:
            entry.expired = True
            send_expired_email(entry.username)
    db.session.commit()


def send_expired_email(username):
    contact = Contacts.query.filter(Contacts.username.like(username)).first()

    msg = MIMEText("One of the classifieds that you posted 180 days ago has been marked as expired.")
    msg['Subject'] = "One of your classifieds has expired"
    msg['From'] = "no-reply@bethel.edu"
    msg['To'] = contact.email

    s = smtplib.SMTP('localhost')
    s.sendmail("no-reply@bethel.edu", [contact.email], msg.as_string())
    s.quit()


def contact_exists_in_db(username):
    return len(list(Contacts.query.filter(Contacts.username.like(username)).all())) > 0


def contact_is_admin(username):
    return Contacts.query.filter(Contacts.username.like(username)).first().isAdmin


def get_non_admins():
    non_admins = Contacts.query.all()
    to_return = []
    for na in non_admins:
        if not na.isAdmin:
            to_return += [{'username': na.username, 'first_name': na.first_name, 'last_name': na.last_name}]
    return to_return


def get_admins():
    admins = Contacts.query.all()
    to_return = []
    for a in admins:
        if a.isAdmin:
            to_return += [{'username': a.username, 'first_name': a.first_name, 'last_name': a.last_name}]
    return to_return


def make_admin(username):
    contact_to_change = Contacts.query.filter(Contacts.username.like(username)).first()
    contact_to_change.isAdmin = True
    db.session.commit()


def remove_admin(username):
    contact_to_change = Contacts.query.filter(Contacts.username.like(username)).first()
    contact_to_change.isAdmin = False
    db.session.commit()


def classified_exists_in_db(id):
    return len(list(Classifieds.query.filter(Classifieds.id.like(id)).all())) > 0
