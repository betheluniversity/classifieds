import datetime
import smtplib
from collections import OrderedDict
from email.mime.text import MIMEText

from classifieds import app, db
from models import Posts, Contacts, Categories, PostCategories
from sqlalchemy import asc, desc, or_


# In general, these methods simply enable loose coupling between the database and the server. Some take in the
# necessary arguments needed by the database that can't be generated, and return the right value, while others are more
# or less void methods that change specific entries in the database for functionality purposes.

#######################################################################################################################
#                                                    Alter Posts                                                      #
#######################################################################################################################

def add_post(title, description, price, username, categories_list):
    try:
        new_post = Posts(title=title, desc=description, price=price, username=username)
        db.session.add(new_post)
        new_post_id = Posts.query.order_by(desc(Posts.id)).first().id
        for category in categories_list:
            category_id = Categories.query.filter(Categories.category_for_html == category).first().id
            row_to_add = PostCategories(new_category_id=category_id, new_post_id=new_post_id)
            db.session.add(row_to_add)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False


def mark_entry_as_complete(entry_id, username):
    entry_to_update = Posts.query.filter(Posts.id.like(entry_id)).first()
    if entry_to_update.username == username or contact_is_admin(username):
        entry_to_update.completed = True
        db.session.commit()


def mark_entry_as_active(entry_id, username):
    entry_to_update = Posts.query.filter(Posts.id.like(entry_id)).first()
    if entry_to_update.username == username or contact_is_admin(username):
        entry_to_update.date_added = datetime.datetime.now()
        entry_to_update.expired = False
        db.session.commit()


def expire_old_posts():
    all_entries = search_posts(completed=False, expired=False)
    for key in all_entries:
        entry = all_entries[key]['post']
        now = datetime.datetime.now().date()
        then = entry.date_added.date()
        if (now - then).days >= 180:
            entry.expired = True
            send_expired_email(entry.username)
    db.session.commit()


def delete_post(post_id):
    deleted = Posts.query.filter_by(id=post_id).delete()
    db.session.commit()
    return deleted


#######################################################################################################################
#                                                     Get Posts                                                       #
#######################################################################################################################


# This method takes the unique identifier of an ad in the DB, then returns it and all its details so that the rendering
# can be done intelligently (e.g., if the poster is viewing it, if it's expired or completed, etc.)
def view_post(post_id):
    post = Posts.query.filter(Posts.id.like(post_id)).first()
    contact = Contacts.query.filter(Contacts.username.like(post.username)).first()
    return {
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'price': post.price,
        'date_added': post.date_added,
        'username': post.username,
        'full_name': contact.first_name + " " + contact.last_name,
        'completed': post.completed,
        'expired': post.expired
    }


def post_exists_in_db(post_id):
    # TODO: use syntax like delete_post method
    return len(list(Posts.query.filter(Posts.id.like(post_id)).all())) > 0


#######################################################################################################################
#                                                   Alter Contacts                                                    #
#######################################################################################################################


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
        db.session.rollback()
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
        db.session.rollback()
        return False


def make_admin(username):
    contact_to_change = Contacts.query.filter(Contacts.username.like(username)).first()
    contact_to_change.is_admin = True
    db.session.commit()


def remove_admin(username):
    contact_to_change = Contacts.query.filter(Contacts.username.like(username)).first()
    contact_to_change.is_admin = False
    db.session.commit()


#######################################################################################################################
#                                                    Get Contacts                                                     #
#######################################################################################################################


def get_contact(username):
    contact = Contacts.query.filter(Contacts.username.like(username)).first()
    return {
        'username': contact.username,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'email': contact.email,
        'phone_number': contact.phone_number
    }


def contact_exists_in_db(username):
    return len(list(Contacts.query.filter(Contacts.username.like(username)).all())) > 0


def contact_is_admin(username):
    return Contacts.query.filter(Contacts.username.like(username)).first().is_admin


def get_non_admins():
    non_admins = Contacts.query.all()
    to_return = []
    for na in non_admins:
        if not na.is_admin:
            to_return.append({'username': na.username, 'first_name': na.first_name, 'last_name': na.last_name})
    return to_return


def get_admins():
    admins = Contacts.query.all()
    to_return = []
    for a in admins:
        if a.is_admin:
            to_return.append({'username': a.username, 'first_name': a.first_name, 'last_name': a.last_name})
    return to_return


#######################################################################################################################
#                                                  Alter Categories                                                   #
#######################################################################################################################


def add_category(html, human):
    try:
        new_category = Categories(category_html=html, category_human=human)
        db.session.add(new_category)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False


#######################################################################################################################
#                                                   Get Categories                                                    #
#######################################################################################################################


def get_category_list(return_list_of_tuples=False):
    raw_list = Categories.query.order_by(asc(Categories.category_for_html)).all()
    if return_list_of_tuples:
        return [(category.category_for_html, category.category_for_humans) for category in raw_list]
    else:
        return [{'category_html': category.category_for_html, 'category_human': category.category_for_humans}
                for category in raw_list]


def get_post_categories(post_id):
    post_category_rows = PostCategories.query.filter(PostCategories.post_id == post_id).all()
    to_return = []
    for post_category in post_category_rows:
        category_row = Categories.query.filter(Categories.id == post_category.category_id).first()
        category_dict = {
            'category_html': category_row.category_for_html,
            'category_human': category_row.category_for_humans
        }
        to_return.append(category_dict)
    return to_return


#######################################################################################################################
#                                                 Database Utilities                                                  #
#######################################################################################################################


# If we want to change this over to pagination at a later date, I'm putting in commented code that should get you
# started on it.
def search_posts(title=[u"%"], description=[u"%"], categories=[u"%"], username=u"%", completed=u"%", expired=u"%",
                 sort_date_descending=True):
    # def search_classifieds(title=u"%", description=u"%", categories=u"%", username=u"%", completed=u"%", expired=u"%",
    #                        max_results=50, page_no=1):
    titles = Posts.title.like(title[0])
    for term in title[1:]:
        titles = or_(titles, Posts.title.like(term))

    descriptions = Posts.description.like(description[0])
    for term in description[1:]:
        descriptions = or_(descriptions, Posts.description.like(term))

    or_categories = Categories.category_for_html.like(categories[0])
    for term in categories[1:]:
        or_categories = or_(or_categories, Categories.category_for_html.like(term))

    if isinstance(completed, bool):
        is_completed = Posts.completed == completed
    else:
        is_completed = Posts.completed.like(completed)

    if isinstance(expired, bool):
        is_expired = Posts.expired == expired
    else:
        is_expired = Posts.expired.like(expired)

    if sort_date_descending:
        ordering = desc(Posts.date_added)
    else:
        ordering = asc(Posts.date_added)

    all_results = db.session.query(Posts, Contacts, PostCategories, Categories
        ).join(Contacts, Contacts.username == Posts.username
        ).join(PostCategories, PostCategories.post_id == Posts.id
        ).join(Categories, Categories.id == PostCategories.category_id
        ).order_by(ordering
        ).filter(
            titles,
            descriptions,
            or_categories,
            Posts.username.like(username),
            is_completed,
            is_expired
        ).all()
    # ).limit(max_results).offset(max_results * (page_no - 1)).all()

    # Each row returned is a tuple of the following:
    # (non-unique post, non-unique contact, unique post_category, non-unique category)
    # This for loop iterates through them to turn it into an ordered dictionary of dictionaries like this:
    # {unique post, non-unique contact, list of non-unique categories}
    to_return = OrderedDict()
    for row in all_results:
        if row[0].id in to_return:
            to_return[row[0].id]['categories'].append(row[3])
        else:
            to_return[row[0].id] = {
                'post': row[0],
                'contact': row[1],
                'categories': [row[3]]
            }
    return to_return


def make_template_friendly_results(search_results):
    to_send = []
    for key in search_results:
        entry = search_results[key]
        entry_dictionary = {
            'id': entry['post'].id,
            'title': entry['post'].title,
            'description': entry['post'].description,
            'price': entry['post'].price,
            'date_added': entry['post'].date_added,
            'username': entry['post'].username,
            'full_name': entry['contact'].first_name + " " + entry['contact'].last_name,
            'completed': entry['post'].completed,
            'expired': entry['post'].expired
        }
        to_send.append(entry_dictionary)
    return to_send


# This method is used for when a poster is looking at all the ads that they've posted, and allows them to sort by the
# status of the post, whether it's active, completed, expired, or all statuses
def filter_posts(username, selector):
    search_params = {
        'username': username,
        'sort_date_descending': False
    }
    if selector == "all":
        pass
    elif selector == "active":
        search_params['completed'] = False
        search_params['expired'] = False
    elif selector == "completed":
        search_params['completed'] = True
    elif selector == "expired":
        search_params['completed'] = False
        search_params['expired'] = True
    elif selector == "external":
        search_params['username'] = u"%@%"
    else:
        pass

    entries = search_posts(**search_params)
    return make_template_friendly_results(entries)


# A nice, generalized query method. Given a dictionary of kwargs, it will search through the existing DB for matching
# terms. If no term is given for a certain column, it will search for the wildcard '%'. All other search terms will be
# searched in a way so that it will do partial matches as well as full matches.
def query_database(params):
    entries = search_posts(**params)
    return make_template_friendly_results(entries)


# This method gets all the active posts, sorts them from most recent to least recent, then returns them as a list to be
# rendered
def get_homepage():
    return query_database({'expired': False, 'completed': False})


def send_expired_email(username):
    contact = Contacts.query.filter(Contacts.username.like(username)).first()

    msg = MIMEText("One of the classifieds that you posted 180 days ago has been marked as expired.")
    msg['Subject'] = "One of your classifieds has expired"
    msg['From'] = "no-reply@bethel.edu"
    msg['To'] = contact.email

    s = smtplib.SMTP('localhost')
    s.sendmail("no-reply@bethel.edu", [contact.email], msg.as_string())
    s.quit()


# A temporary method for the early stages of the new website so that users have a convenient way to provide feedback
def send_feedback_email(form_contents, username):
    msg = MIMEText(form_contents['input'])
    msg['Subject'] = "Feedback regarding classifieds.bethel.edu from " + username
    msg['From'] = "classifieds@bethel.edu"
    msg['To'] = app.config['ADMINS']

    s = smtplib.SMTP('localhost')
    s.sendmail(username + "@bethel.edu", app.config['ADMINS'], msg.as_string())
    s.quit()
