import datetime
import smtplib
from collections import OrderedDict
from email.mime.text import MIMEText
from sqlalchemy import asc, desc, or_

from classifieds import app, db
from models import Posts, Contacts, Categories, PostCategories


# In general, these methods simply enable loose coupling between the database and the server. Some take in the
# necessary arguments needed by the database that can't be generated, and return the right value, while others are more
# or less void methods that change specific entries in the database for functionality purposes.

#######################################################################################################################
#                                                    Alter Posts                                                      #
#######################################################################################################################

def add_post(new_title, new_description, new_price, username, new_categories_list):
    try:
        new_post = Posts(title=new_title, desc=new_description, price=new_price, username=username)
        db.session.add(new_post)
        new_post_id = Posts.query.order_by(desc(Posts.id)).first().id
        for category in new_categories_list:
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


def renew_entry(entry_id, username):
    entry_to_update = Posts.query.filter(Posts.id.like(entry_id)).first()
    if entry_to_update.username == username or contact_is_admin(username):
        entry_to_update.date_added = datetime.datetime.now()
        entry_to_update.expired = False
        db.session.commit()


def expire_old_posts():
    all_active_entries = search_posts(completed=False, expired=False)
    for key in all_active_entries:
        entry = all_active_entries[key]['post']
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
    posts = Posts.query.filter(Posts.id.like(post_id)).all()
    return len(list(posts)) > 0


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
    contacts = Contacts.query.filter(Contacts.username.like(username)).all()
    return len(list(contacts)) > 0


def contact_is_admin(username):
    return Contacts.query.filter(Contacts.username.like(username)).first().is_admin


def get_non_admins():
    non_admins = Contacts.query.filter(not Contacts.is_admin).all()
    return [{'username': na.username, 'first_name': na.first_name, 'last_name': na.last_name}
            for na in non_admins]


def get_admins():
    admins = Contacts.query.filter(Contacts.is_admin).all()
    return [{'username': a.username, 'first_name': a.first_name, 'last_name': a.last_name}
            for a in admins]


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
    #                        sort_date_descending=True, max_results=50, page_no=1):

    # There's always a list of titles; by default it's only the wildcard, but this will search for any title that
    # contains any word in the list
    titles = Posts.title.like(title[0])
    for term in title[1:]:
        titles = or_(titles, Posts.title.like(term))

    # Similar to title, description searches for wildcard by default, but can search for any descriptions that contain
    # any word in its list
    descriptions = Posts.description.like(description[0])
    for term in description[1:]:
        descriptions = or_(descriptions, Posts.description.like(term))

    # This filter functions similarly to title and description, but instead searches for exact matches between any of
    # the html_categories passed in by the list and the Categories table
    or_categories = Categories.category_for_html.like(categories[0])
    for term in categories[1:]:
        or_categories = or_(or_categories, Categories.category_for_html.like(term))

    # If a boolean value is specified, only return posts that match that value. Otherwise, it searches for a wildcard,
    # allowing it to return rows with either True or False values
    if isinstance(completed, bool):
        is_completed = Posts.completed == completed
    else:
        is_completed = Posts.completed.like(completed)

    if isinstance(expired, bool):
        is_expired = Posts.expired == expired
    else:
        is_expired = Posts.expired.like(expired)

    # Home page and search results return with most recent date at the top, but viewing user's posts should have the
    # oldest date at the top. By having the sort done in this method, it clears up the code elsewhere.
    if sort_date_descending:
        ordering = desc(Posts.date_added)
    else:
        ordering = asc(Posts.date_added)

    # This monstrosity is what joins all 4 tables together properly, adds the filters as specified above, and then runs
    # the resultant query.
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
    #   ).limit(max_results).offset(max_results * (page_no - 1)).all()

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


def query_database(params):
    entries = search_posts(**params)
    return make_template_friendly_results(entries)


def get_homepage():
    return query_database({'expired': False, 'completed': False})


#######################################################################################################################
#                                                   Email Methods                                                     #
#######################################################################################################################


def send_expired_email(username):
    contact = Contacts.query.filter(Contacts.username.like(username)).first()

    msg = MIMEText("One of the classifieds that you posted 180 days ago has been marked as expired.")
    msg['Subject'] = "One of your classifieds has expired"
    msg['From'] = "no-reply@bethel.edu"
    msg['To'] = contact.email

    s = smtplib.SMTP('localhost')
    s.sendmail("no-reply@bethel.edu", [contact.email], msg.as_string())
    s.quit()


def send_feedback_email(form_contents, username):
    msg = MIMEText(form_contents['input'])
    msg['Subject'] = "Feedback regarding classifieds.bethel.edu from " + username
    msg['From'] = "classifieds@bethel.edu"
    msg['To'] = app.config['ADMINS']

    s = smtplib.SMTP('localhost')
    s.sendmail(username + "@bethel.edu", app.config['ADMINS'], msg.as_string())
    s.quit()