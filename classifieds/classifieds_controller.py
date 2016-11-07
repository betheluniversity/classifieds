import datetime
import smtplib
from email.mime.text import MIMEText

from classifieds import db, Posts, Contacts
from sqlalchemy import or_, desc


# In general, these methods simply enable loose coupling between the database and the server. Some take in the
# necessary arguments needed by the database that can't be generated, and return the right value, while others are more
# or less void methods that change specific entries in the database for functionality purposes.


def add_post(title, description, price, categories, username):
    new_post = Posts(title=title, desc=description, price=price, categories=categories, username=username)
    try:
        db.session.add(new_post)
        db.session.commit()
    except:
        return False
    return True


def add_contact(username, first_name, last_name, email, phone_number):
    # If the username is already in here, it should fail.
    try:
        existing_info = Contacts.query.filter(Contacts.username.like(username)).first()
        if existing_info is None:
            new_contact = Contacts(username=username, first=first_name, last=last_name, email=email,
                                   phone=phone_number)
            db.session.add(new_contact)
            db.session.commit()
            return True
        else:
            return False
    except:
        return False


def update_contact(username, first_name, last_name, email, phone_number):
    # If the username is not already in here, it should fail
    try:
        existing_info = Contacts.query.filter(Contacts.username.like(username)).first()
        if existing_info is not None:
            existing_info.first_name = first_name
            existing_info.last_name = last_name
            existing_info.email = email
            existing_info.phone_number = phone_number
            db.session.commit()
            return True
        else:
            return False
    except:
        return False


def get_contact(username):
    contact = Contacts.query.filter(Contacts.username.like(username)).first()
    to_return = {
        'username': contact.username,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'email': contact.email,
        'phone_number': contact.phone_number
    }
    return to_return


def mark_entry_as_complete(entry_id, username):
    entry_to_update = Posts.query.filter(Posts.id.like(entry_id)).first()
    if entry_to_update.username == username or contact_is_admin(username):
        entry_to_update.completed = True
        db.session.commit()


def mark_entry_as_active(entry_id, username):
    entry_to_update = Posts.query.filter(Posts.id.like(entry_id)).first()
    if entry_to_update.username == username or contact_is_admin(username):
        entry_to_update.dateAdded = datetime.datetime.now()
        entry_to_update.expired = False
        db.session.commit()

# TODO: re-work this search function to work with the new categories table
# If we want to change this over to pagination at a later date, I'm putting in commented code that should get you
# started on it.
def search_posts(title=u"%", description=u"%", categories=u"%", username=u"%", completed=u"%", expired=u"%"):
    # def search_classifieds(title=u"%", description=u"%", categories=u"%", username=u"%", completed=u"%", expired=u"%",
    #                        max_results=50, page_no=1):
    if isinstance(title, list):
        titles = Posts.title.like(u'%' + title[0] + u'%')
        for term in title[1:]:
            titles = or_(titles, Posts.title.like(u'%' + term + u'%'))
    else:
        titles = Posts.title.like(title)

    if isinstance(description, list):
        descriptions = Posts.description.like(u'%' + description[0] + u'%')
        for term in description[1:]:
            descriptions = or_(descriptions, Posts.description.like(u'%' + term + u'%'))
    else:
        descriptions = Posts.description.like(description)

    # if isinstance(categories, list):
    #     or_categories = Posts.categories.like(u'%' + categories[0] + u'%')
    #     for term in categories[1:]:
    #         or_categories = or_(or_categories, Posts.categories.like(u'%' + term + u'%'))
    # else:
    #     or_categories = Posts.categories.like(categories)

    if completed == u"%":
        completed = Posts.completed.like(completed)
    elif isinstance(completed, bool):
        completed = Posts.completed == completed

    if expired == u"%":
        expired = Posts.expired.like(expired)
    elif isinstance(expired, bool):
        expired = Posts.expired == expired

    return Posts.query.join(Contacts, Contacts.username == Posts.username).add_columns(Contacts.first_name,
        Contacts.last_name).order_by(desc(Posts.dateAdded)).filter(
            titles, descriptions, Posts.username.like(username),
            completed, expired
    ).all()
    # ).limit(max_results).offset(max_results * (page_no - 1)).all()


def get_category_list():
    # TODO: implement a "SELECT * FROM CATEGORIES;" query here
    return []


def expire_old_posts():
    all_entries = search_posts(completed=False, expired=False)
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
            to_return.append({'username': na.username, 'first_name': na.first_name, 'last_name': na.last_name})
    return to_return


def get_admins():
    admins = Contacts.query.all()
    to_return = []
    for a in admins:
        if a.isAdmin:
            to_return.append({'username': a.username, 'first_name': a.first_name, 'last_name': a.last_name})
    return to_return


def make_admin(username):
    contact_to_change = Contacts.query.filter(Contacts.username.like(username)).first()
    contact_to_change.isAdmin = True
    db.session.commit()


def remove_admin(username):
    contact_to_change = Contacts.query.filter(Contacts.username.like(username)).first()
    contact_to_change.isAdmin = False
    db.session.commit()


def delete_classfieid(classified_id):
    deleted = Posts.query.filter_by(id=classified_id).delete()
    db.session.commit()
    return deleted


def classified_exists_in_db(id):
    # todo use syntax like delete_classfieid method
    return len(list(Classifieds.query.filter(Classifieds.id.like(id)).all())) > 0
