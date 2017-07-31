__all__ = [
    'add_category',
    'add_contact',
    'add_post',
    'allowed_to_edit_post',
    'contact_exists_in_db',
    'contact_is_admin',
    'create_page_selector_packet',
    'delete_category',
    'delete_post',
    'edit_category',
    'edit_contact',
    'edit_post',
    'expire_old_posts',
    'filter_posts',
    'get_admins',
    'get_category',
    'get_category_form_data',
    'get_category_list',
    'get_contact',
    'get_contact_form_data',
    'get_homepage',
    'get_non_admins',
    'get_post',
    'get_post_categories',
    'get_post_form_data',
    'make_admin',
    'mark_entry_as_complete',
    'post_exists_in_db',
    'query_database',
    'remove_admin',
    'renew_entry',
    'search_for_external_posts',
    'send_feedback_email'
]

# Standard library imports
import datetime
import math
import os
import re
import smtplib

# Third party imports
from collections import OrderedDict
# from ordereddict import OrderedDict
from email.mime.text import MIMEText
from sqlalchemy import asc, desc, or_
from werkzeug.datastructures import ImmutableMultiDict

# Local application imports
from app import app, db
from models import Posts, Contacts, Categories, PostCategories


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
    except Exception as e:
        db.session.rollback()
        print e.message
        return False


def edit_post(post_id, title, description, price, categories_list):
    try:
        # Edit the values in the post itself
        existing_post = Posts.query.filter(Posts.id.like(post_id)).first()
        if existing_post:
            existing_post.title = title
            existing_post.description = description
            existing_post.price = price
        else:
            return False

        # Delete existing PostCategory rows and make new ones
        PostCategories.query.filter_by(post_id=post_id).delete()

        for category in categories_list:
            category_id = Categories.query.filter(Categories.category_for_html == category).first().id
            row_to_add = PostCategories(new_category_id=category_id, new_post_id=post_id)
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
    all_active_entries = _search_posts(completed=False, expired=False, return_all_results=True)[0]
    for row_dict in all_active_entries:
        entry = row_dict['post']
        now = datetime.datetime.now().date()
        then = entry.date_added.date()
        if (now - then).days >= app.config['EXPIRY']:
            Posts.query.filter(Posts.id.like(entry.id)).first().expired = True
            _send_expired_email(entry.username, entry.id)
    db.session.commit()


def delete_post(post_id):
    try:
        postcateory_rows_for_this_post = PostCategories.query.filter_by(post_id=post_id).all()
        for row in postcateory_rows_for_this_post:
            PostCategories.query.filter_by(id=row.id).delete()
        deleted = Posts.query.filter_by(id=post_id).delete()
        db.session.commit()
        return deleted
    except Exception as e:
        db.session.rollback()
        print e.message
        return False


#######################################################################################################################
#                                                     Get Posts                                                       #
#######################################################################################################################


def get_post_form_data(post_id=None, hidden_username=None):
    if post_id:
        to_return = get_post(post_id)
        to_return['submitters_username'] = to_return['username']
        del to_return['username']
        to_return['categories'] = []
        for cat in get_post_categories(post_id):
            to_return['categories'].append(cat['category_html'])
    else:
        to_return = {'post_id': -1, 'submitters_username': hidden_username}
    return ImmutableMultiDict(to_return)


def get_post(post_id):
    post = Posts.query.filter(Posts.id.like(post_id)).first()
    contact = Contacts.query.filter(Contacts.username.like(post.username)).first()
    return {
        'post_id': post.id,
        'title': post.title,
        'description': post.description,
        'price': post.price,
        'date_added': post.date_added,
        'username': post.username,
        'full_name': contact.first_name + ' ' + contact.last_name,
        'completed': post.completed,
        'expired': post.expired
    }


def post_exists_in_db(post_id):
    posts = Posts.query.filter(Posts.id.like(post_id)).all()
    return len(list(posts)) > 0


def allowed_to_edit_post(post_id, username):
    if contact_is_admin(username):
        return True
    else:
        post = get_post(post_id)
        if post['username'] == username:
            return True
        else:
            return False


#######################################################################################################################
#                                                   Alter Contacts                                                    #
#######################################################################################################################


def add_contact(username, first_name, last_name, email, phone_number):
    # If the username is already in here, it should fail.
    try:
        existing_info = Contacts.query.filter(Contacts.username.like(username)).first()
        if existing_info is None:
            new_contact = Contacts(username=username, first=first_name, last=last_name, email=email, phone=phone_number)
            db.session.add(new_contact)
            db.session.commit()
            return True
        else:
            return False
    except:
        db.session.rollback()
        return False


def edit_contact(username, first_name, last_name, email, phone_number):
    # If the username is not already in here, it should fail
    try:
        existing_info = Contacts.query.filter(Contacts.username.like(username)).first()
        if existing_info:
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


# This method should not have any endpoint; this method is only for usage via terminal
def _delete_contact(username):
    try:
        posts_by_this_user = Posts.query.filter_by(username=username).all()
        for row in posts_by_this_user:
            Posts.query.filter_by(id=row.id).delete()
        Contacts.query.filter_by(username=username).delete()
        db.session.commit()
        return 'Contact and posts successfully deleted'
    except Exception as e:
        db.session.rollback()
        print e.message
        return False


#######################################################################################################################
#                                                    Get Contacts                                                     #
#######################################################################################################################


def get_contact_form_data(username):
    return ImmutableMultiDict(get_contact(username))


def get_contact(username):
    contact = Contacts.query.filter(Contacts.username.like(username)).first()
    return {
        'username': contact.username,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'email': contact.email,
        'phone_number': contact.phone_number,
        'external': contact.username == contact.email
    }


def contact_exists_in_db(username):
    contacts = Contacts.query.filter(Contacts.username.like(username)).all()
    return len(list(contacts)) > 0


def contact_is_admin(username):
    return Contacts.query.filter(Contacts.username.like(username)).first().is_admin


# Although it could be written as .filter(not Contacts.is_admin), it doesn't work properly that way.
def get_non_admins():
    non_admins = Contacts.query.filter(Contacts.is_admin == False).all()
    return [{'username': na.username, 'first_name': na.first_name, 'last_name': na.last_name}
            for na in non_admins]


# Although it could be written as .filter(Contacts.is_admin), it doesn't work properly that way.
def get_admins():
    admins = Contacts.query.filter(Contacts.is_admin == True).all()
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


def edit_category(category_id, new_html, new_human):
    try:
        existing_category = Categories.query.filter(Categories.id.like(category_id)).first()
        if existing_category:
            existing_category.category_for_html = new_html
            existing_category.category_for_humans = new_human
            db.session.commit()
            return True
        else:
            return False
    except:
        db.session.rollback()
        return False


def delete_category(category_id):
    try:
        posts_that_have_this_category = db.session.query(Posts, PostCategories, Categories
            ).join(PostCategories, PostCategories.post_id == Posts.id
            ).join(Categories, PostCategories.category_id == Categories.id
            ).filter(
                Categories.id == category_id
            ).all()
        dict_of_posts = {}
        for post in posts_that_have_this_category:
            # This if statement might be redundant?
            if post[0].id not in dict_of_posts:  # Make sure to only do each post once
                categories_for_this_post = PostCategories.query.filter(PostCategories.post_id == post[0].id).all()
                if len(categories_for_this_post) > 1:
                    # The post_category row with this category can be deleted
                    for post_category in categories_for_this_post:
                        if post_category.category_id == category_id:
                            PostCategories.query.filter_by(id=post_category.id).delete()
                            break
                else:
                    # This is the only category for this post, so it should be changed to 'general' (category.id = 9)
                    post_category_row = PostCategories.query.filter_by(id=categories_for_this_post[0].id).first()
                    post_category_row.category_id = 9
                dict_of_posts[post[0].id] = 'post has been processed'
        # Now that all references to this category have been removed, delete it without fear of Foreign Key dependency
        deleted = Categories.query.filter_by(id=category_id).delete()
        db.session.commit()
        return deleted
    except Exception as e:
        db.session.rollback()
        print e.message
        return False


#######################################################################################################################
#                                                   Get Categories                                                    #
#######################################################################################################################


def get_category_form_data(category_id=None):
    if category_id:  # Get an existing category by ID
        to_return = get_category(category_id)
    else:  # Create a form for a new category
        to_return = {'category_id': -1}

    return ImmutableMultiDict(to_return)


def get_category(category_id):
    category = Categories.query.filter(Categories.id.like(category_id)).first()
    return {
        'category_id': category.id,
        'category_html': category.category_for_html,
        'category_human': category.category_for_humans
    }


def get_category_list(return_list_of_tuples=False):
    raw_list = Categories.query.order_by(asc(Categories.category_for_html)).all()
    if return_list_of_tuples:
        return [(category.category_for_html, category.category_for_humans) for category in raw_list]
    else:
        return [{'category_id': category.id, 'category_html': category.category_for_html, 'category_human': category.category_for_humans}
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


def _search_posts(title=u'%', description=u'%', categories=[u'%'], username=u'%', completed=u'%', expired=u'%',
                  max_results=20, page_no=1, sort_type='sortByDateAZ', return_all_results=False):

    stop_words = _get_stop_words()

    # By default title will be the wildcard, but if it's not then it's assumed to be a string of at least one word
    if title == u'%':
        titles = Posts.title.like(title)
    else:
        # Split the long string of multiple words into a list of individual words wrapped by wildcard characters
        # Don't search for trivial words like "the" or "a" (referred to as stopwords)
        titles_list = [u'%' + t + u'%' for t in title.split(' ') if t not in stop_words]
        # There must be at least one word that is not a stopword
        if len(titles_list) > 0:
            titles = Posts.title.like(titles_list[0])
            for term in titles_list[1:]:
                titles = or_(titles, Posts.title.like(term))
        else:
            titles = Posts.title.like(u'%')

    # Similarly to title, description searches for wildcard by default, but can search for any descriptions that contain
    # any word in its list (excluding stopwords)
    if description == u'%':
        descriptions = Posts.description.like(description)
    else:
        descriptions_list = [u'%' + d + u'%' for d in description.split(' ') if d not in stop_words]
        if len(descriptions_list) > 0:
            descriptions = Posts.description.like(descriptions_list[0])
            for term in descriptions_list[1:]:
                descriptions = or_(descriptions, Posts.description.like(term))
        else:
            descriptions = Posts.description.like(u'%')

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
    ordering = desc(Posts.date_added)

    if sort_type == 'sortByUsernameAZ':
        ordering = asc(Posts.username)
    elif sort_type == 'sortByUsernameZA':
        ordering = desc(Posts.username)
    elif sort_type == 'sortByDateAZ':
        ordering = desc(Posts.date_added)
    elif sort_type == 'sortByDateZA':
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

    # This method takes in the price field given, parses and returns out the numeric value. Entries that lack a number
    # are assigned a price of 0.
    def get_numerical_value(price_string):
        # "I'm sorry" - Nathan Li, 2017
        # This regular expression matches a group of text, numbers (including commas and periods), more text,
        # more numbers, and finally another set of text.
        pattern = '[~@!:$<> &-/a-zA-Z]*(\d[\d,.]*)?[~@!:$<> &-/a-zA-Z]*(\d[\d,.]*)?[~@!:$<> &-/a-zA-Z]*'

        results = re.match(pattern, price_string)
        if results is not None:
            # Because the primary/lower price should always be on the left, get the left number group match
            number_string = results.groups()[0]
            if number_string is None:
                return 0
            return float(number_string.replace(',', ''))
        else:
            # If there is no match, that means the price is a word which equates to 0 numerically
            return 0

    def get_sortable_text_from_string(silly_string):
        pattern = '^[^\w]*(.*)'
        results = re.match(pattern, silly_string)
        return results.groups()[0].upper()

    # The sorted function here takes in all results processed into numbers and sorts them accordingly by price.
    # The sorting is simply reversed for reverse price order.
    if sort_type == 'sortByTitleAZ':
        all_results = sorted(
            all_results,
            key=lambda tuple_result: get_sortable_text_from_string(tuple_result[0].title)
        )
    elif sort_type == 'sortByTitleZA':
        all_results = sorted(
            all_results,
            key=lambda tuple_result: get_sortable_text_from_string(tuple_result[0].title),
            reverse=True
        )
    elif sort_type == 'sortByDescriptionAZ':
        all_results = sorted(
            all_results,
            key=lambda tuple_result: get_sortable_text_from_string(tuple_result[0].description)
        )
    elif sort_type == 'sortByDescriptionZA':
        all_results = sorted(
            all_results,
            key=lambda tuple_result: get_sortable_text_from_string(tuple_result[0].description),
            reverse=True
        )
    elif sort_type == 'sortByPriceAZ':
        all_results = sorted(
            all_results,
            key=lambda tuple_result: get_numerical_value(tuple_result[0].price)
        )
    elif sort_type == 'sortByPriceZA':
        all_results = sorted(
            all_results,
            key=lambda tuple_result: get_numerical_value(tuple_result[0].price),
            reverse=True
        )

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

    num_results = len(to_return)
    starting_index = max_results * (page_no - 1)
    if return_all_results:
        to_return = [to_return[key] for key in to_return.keys()]
    else:
        to_return = [to_return[key] for key in to_return.keys()[starting_index:starting_index + max_results]]

    return to_return, int(math.ceil(float(num_results)/float(max_results)))


def search_for_external_posts(name_or_email):
    if len(name_or_email) > 0:
        words = name_or_email.split(' ')
        first_name = Contacts.first_name.like('%' + words[0] + '%')
        last_name = Contacts.last_name.like('%' + words[0] + '%')
        username = or_(Contacts.username.like('%' + words[0] + '%@%'),
                       Contacts.username.like('%@%' + words[0] + '%'))
        for word in words[1:]:
            name = '%' + word + '%'
            email_one = '%' + word + '%@%'
            email_two = '%@%' + word + '%'
            first_name = or_(first_name, Contacts.first_name.like(name))
            last_name = or_(last_name, Contacts.last_name.like(name))
            email_or = or_(Contacts.username.like(email_one), Contacts.username.like(email_two))
            username = or_(username, email_or)
    else:
        first_name = Contacts.first_name.like('%')
        last_name = Contacts.last_name.like('%')
        username = Contacts.username.like('%@%')

    criteria = or_(or_(first_name, last_name), username)

    all_results = db.session.query(Posts, Contacts, PostCategories, Categories
        ).join(Contacts, Contacts.username == Posts.username
        ).join(PostCategories, PostCategories.post_id == Posts.id
        ).join(Categories, Categories.id == PostCategories.category_id
        ).filter(
            criteria,
            Posts.username.like('%@%'),
            Posts.completed == False,
            # desc(Posts.date_added),  # This line throws a SQL error that I'm not going to fix right now.
        ).all()

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
    to_return = [to_return[key] for key in to_return.keys()]
    return _make_template_friendly_results(to_return)


def _make_template_friendly_results(search_results):
    to_send = []
    for entry in search_results:
        entry_dictionary = {
            'post_id': entry['post'].id,
            'title': entry['post'].title,
            'description': entry['post'].description,
            'price': entry['post'].price,
            'date_added': entry['post'].date_added,
            'username': entry['post'].username,
            'full_name': entry['contact'].first_name + ' ' + entry['contact'].last_name,
            'completed': entry['post'].completed,
            'expired': entry['post'].expired
        }
        to_send.append(entry_dictionary)
    return to_send


def filter_posts(username, selector, page_number):
    search_params = {
        'username': username,
        'page_no': page_number
    }
    if selector == 'all':
        pass
    elif selector == 'active':
        search_params['completed'] = False
        search_params['expired'] = False
    elif selector == 'completed':
        search_params['completed'] = True
    elif selector == 'expired':
        search_params['completed'] = False
        search_params['expired'] = True
    elif selector == 'external':
        search_params['username'] = u'%@%'
    else:
        pass

    entries, number_of_pages = _search_posts(**search_params)
    return _make_template_friendly_results(entries), number_of_pages


def query_database(params):
    entries, num_pages = _search_posts(**params)
    return _make_template_friendly_results(entries), num_pages


def get_homepage(page_number, sort_type):
    return query_database({'expired': False, 'completed': False, 'page_no': page_number, 'sort_type': sort_type})


#######################################################################################################################
#                                                   Other Methods                                                     #
#######################################################################################################################


def get_app_settings():
    to_return = {}
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
    final_path = os.path.join(parent_dir_path, 'app_settings.py')
    with open(final_path) as f:
        for line in f.readlines():
            key, val = line.split(' = ')
            to_return[key] = val[1:-2]  # This peels off a ' from the front and a '\n from the end
    return to_return


def _get_stop_words():
    to_return = []
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
    final_path = os.path.join(parent_dir_path, 'search_keywords_to_ignore.txt')
    with open(final_path) as f:
        for line in f.readlines():
            to_return.append(line[:-1])
    return to_return


def create_page_selector_packet(number_of_pages, selected_page, sort_type='reverseDateOrder'):
    previous_page_number = max(1, (selected_page - 1))  # Must always be 1 or greater
    next_page_number = min((selected_page + 1), number_of_pages)  # Can never be more than the last page

    DESIRED_OFFSET = 2
    if number_of_pages < 2 * DESIRED_OFFSET + 2:  # window = 2 * desired_offset + 1, so x < (window + 1)
        page_range = range(1, number_of_pages + 1)
    else:
        if selected_page < DESIRED_OFFSET + 1:
            page_range = range(1, 2 * DESIRED_OFFSET + 2)  # window = 2 * desired_offset + 1, then offset by +1
        elif number_of_pages - selected_page < DESIRED_OFFSET + 1:
            page_range = range(number_of_pages - 2 * DESIRED_OFFSET, number_of_pages+1)
        else:
            page_range = range(selected_page - DESIRED_OFFSET, selected_page + DESIRED_OFFSET + 1)

    page_selector_packet = {
        'previous': previous_page_number,
        'current': selected_page,
        'next': next_page_number,
        'last': number_of_pages,
        'all_page_numbers': page_range,
        'sort_type': sort_type
    }
    return page_selector_packet


def _send_expired_email(username, post_id):
    contact = Contacts.query.filter(Contacts.username.like(username)).first()

    msg = MIMEText('One of the posts that you listed ' + str(app.config['EXPIRY']) +
                   ' days ago in ' + app.config['SITE_NAME'] + ' has been marked as expired. If you want, you can' +
                   ' renew it at https://' + app.config['SITE_URL'] + '/view-post/' + str(post_id))
    msg['Subject'] = 'One of your posts has expired'
    msg['From'] = 'no-reply@bethel.edu'
    msg['To'] = contact.email

    s = smtplib.SMTP('localhost')
    s.sendmail('no-reply@bethel.edu', [contact.email], msg.as_string())
    s.quit()


def send_feedback_email(form_contents, username):
    msg = MIMEText(form_contents['input'])
    msg['Subject'] = 'Feedback from ' + username
    msg['From'] = 'webmaster@bethel.edu'
    msg['To'] = app.config['ADMINS']

    s = smtplib.SMTP('localhost')
    s.sendmail(username + '@bethel.edu', app.config['ADMINS'], msg.as_string())
    s.quit()
