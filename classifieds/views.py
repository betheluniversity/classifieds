from controller import *
from flask import abort, redirect, render_template, request, session
from flask_classy import FlaskView, route
from forms import RegularPostForm, ExternalPosterForm, ContactForm, CategoryForm


# This Flask-Classy object is simply named "View" because Flask-Classy takes whatever is in front of View and makes it
# the first argument of the url, such that "ClassifiedsView" would be accessed via classifieds.bethel.edu/classifieds
# To avoid that, I put nothing in front of "View" so now all the URLs will have the form classifieds.bethel.edu/url-name
class View(FlaskView):

    ###################################################################################################################
    #                                        Endpoints that display lists of posts                                    #
    ###################################################################################################################

    # This method doesn't need the actual word index; just the base URL will work to return the homepage
    def index(self):
        page_number = request.args.get('page')  # Needs to be an int > 0
        if page_number is None:
            page_number = 1
        else:
            page_number = int(page_number)

        sort_type = request.args.get('sort')
        if sort_type is None:
            sort_type = "reverseDateOrder"

        results, number_of_pages = get_homepage(page_number, sort_type)
        page_selector_packet = create_page_selector_packet(number_of_pages, page_number, sort_type)
        return render_template("homepage.html",
                               values=results,
                               page_selector=page_selector_packet,
                               list_of_sort_types=app.config['SORT_TYPES'],
                               showStatus=False)

    # This URL is only for rendering to a channel in BLink
    @route("/blink-posts")
    def blink_posts(self):
        results, num_pages = get_homepage(1, "reverseDateOrder")
        return render_template("blink_template.html", values=results, showStatus=False)

    # This method is more or less a 'hub' for all the various ways that a poster would like to view the posts that
    # they've made. This passes on what type of posts they want to see, the DB does the filtering and returns the list,
    # and they all get rendered the same way. This is how administrators can view all external posts in one area.
    @route("/view-posted/<selector>")
    def view_posted(self, selector):
        if selector not in ["all", "active", "completed", "expired", "external"]:
            return abort(404)
        if selector == "external" and not contact_is_admin(session['username']):
            return abort(404)
        if contact_exists_in_db(session['username']):
            page_number = request.args.get('page')  # Needs to be an int > 0
            if page_number is None:
                page_number = 1
            else:
                page_number = int(page_number)

            results, number_of_pages = filter_posts(session['username'], selector, page_number)
            page_selector_packet = create_page_selector_packet(number_of_pages, page_number)
            page_selector_packet['sort_type'] = ""
            return render_template("view/users_posts.html", posts=results, page_selector=page_selector_packet)
        else:
            error_message = "You don't exist in the contacts database yet, and as such you don't have any posts to view."
            return render_template("error_page.html", error=error_message)

    # Really straightforward method, simply renders the search page.
    @route("/search-page")
    def search_page(self):
        return render_template("search_page.html", categories=get_category_list())

    # This method does a bit of work in preparation of the DB query; it creates a dictionary of search terms that are
    # keyed to match the keyword arguments of the DB search method in forms. It creates a list of all the words being
    # searched for, and pads both sides of the title words and description words with a '%' for partial matching in the
    # DB. Categories, on the other hand, have to have an exact match. It can only return active posts.
    @route("/search", methods=['POST'])
    @route("/search/<category>", methods=['GET'])
    def search(self, category=None):
        to_send = {
            'expired': False,
            'completed': False
        }
        if request.method == 'POST':
            storage = request.form
            to_send['sort_type'] = storage['sort_type']
            if len(storage['title']) > 0:
                to_send['title'] = [u"%" + word + u"%" for word in storage['title'].split(" ")]
            if len(storage['description']) > 0:
                to_send['description'] = [u"%" + word + u"%" for word in storage['description'].split(" ")]
            category_list = storage.getlist('categories[]')
            if len(category_list) > 0:
                to_send['categories'] = category_list
            page_number = int(storage['page_number'])
            to_send['page_no'] = page_number

            results, number_of_pages = query_database(to_send)
            page_selector_packet = create_page_selector_packet(number_of_pages, page_number, to_send['sort_type'])
            return render_template("search_results.html",
                                   values=results,
                                   page_selector=page_selector_packet,
                                   list_of_sort_types=app.config['SORT_TYPES'])
        else:
            to_send['categories'] = [category]
            page_number = request.args.get('page')  # Needs to be an int > 0
            if page_number is None:
                page_number = 1
            else:
                page_number = int(page_number)

            to_send['page_no'] = page_number
            results, number_of_pages = query_database(to_send)
            page_selector_packet = create_page_selector_packet(number_of_pages, page_number)
            return render_template("homepage.html",
                                   values=results,
                                   page_selector=page_selector_packet,
                                   list_of_sort_types=app.config['SORT_TYPES'],
                                   showStatus=False)

    ###################################################################################################################
    #                                                  Post endpoints                                                 #
    ###################################################################################################################

    # This method is pretty straightforward, just checks if the id they're requesting exists. If it does, it renders it.
    # The template renderer itself takes care of the ad's expired/completed status, if it's the original poster, etc.
    @route("/view-post/<post_id>")
    def view_post(self, post_id):
        if post_exists_in_db(post_id):
            return render_template("view/post.html", post=get_post(post_id), categories=get_post_categories(post_id))
        else:
            error_message = "That post id number doesn't exist in the posts database."
            return render_template("error_page.html", error=error_message)

    # This URL is to get the post form so that the user can fill it out and submit it to the DB
    @route("/add-post")
    def add_post(self):
        if contact_exists_in_db(session['username']):
            return render_template("forms/post.html",
                                   form=RegularPostForm(get_post_form_data(hidden_username=session['username'])),
                                   external=False, new=True)
        else:
            error_message = "You don't exist in the contacts database yet, and as such you cannot submit a post."
            return render_template("error_page.html", error=error_message)

    @route("/edit-post/<post_id>")
    def edit_post(self, post_id):
        if contact_exists_in_db(session['username']):
            if post_exists_in_db(post_id):
                if allowed_to_edit_post(post_id, session['username']):
                    return render_template("forms/post.html",
                                           form=RegularPostForm(get_post_form_data(post_id=post_id)),
                                           external=False, new=False)
                else:
                    error_message = "You don't have permission to edit that post."
                    return render_template("error_page.html", error=error_message)
            else:
                error_message = "That post id number doesn't exist in the posts database."
                return render_template("error_page.html", error=error_message)
        else:
            error_message = "You don't exist in the contacts database yet, and as such you cannot edit a post."
            return render_template("error_page.html", error=error_message)

    # This is a post method that takes the post form's contents, parses them, validates, and if it passes, it adds
    # it to the DB and then returns if it was successful or not.
    @route("/submit-post", methods=['POST'])
    def submit_post(self):
        form_contents = request.form
        data_for_new_post = {
            'post_id': form_contents.get('id'),
            'username': form_contents.get('submitters_username'),
            'title': form_contents.get('title'),
            'description': form_contents.get('description'),
            'price': form_contents.get('price'),
            'categories_list': form_contents.getlist('categories')
        }
        if not contact_exists_in_db(data_for_new_post['username']):
            error_message = "You don't exist in the contacts database yet, and as such you cannot submit a post."
            return render_template("error_page.html", error=error_message)

        if '@' in data_for_new_post['username']:
            form = ExternalPosterForm(form_contents)
        else:
            form = RegularPostForm(form_contents)
        is_valid = form.validate()
        if not is_valid:
            return render_template("forms/post.html", form=form)

        if data_for_new_post['post_id'] == '-1':  # Submitting a new post
            del data_for_new_post['post_id']
            successfully_submitted = add_post(**data_for_new_post)
            if successfully_submitted:
                message = "Post successfully submitted!"
                return render_template("confirmation_page.html", message=message)
            else:
                error_message = "The post did not get added correctly. Please try again."
                return render_template("error_page.html", error=error_message)
        else:  # Editing an existing post
            del data_for_new_post['username']
            successfully_edited = edit_post(**data_for_new_post)
            if successfully_edited:
                message = "Post successfully edited!"
                return render_template("confirmation_page.html", message=message)
            else:
                error_message = "The post did not get edited correctly. Please try again."
                return render_template("error_page.html", error=error_message)

    # A pretty straightforward pair of methods; if the poster calls this URL via a link on the pages, it will change
    # that value appropriately in the DB.
    @route("/mark-complete/<post_id>")
    def mark_complete(self, post_id):
        mark_entry_as_complete(post_id, session['username'])
        return redirect('/view-posted/active')

    def renew(self, post_id):
        renew_entry(post_id, session['username'])
        return redirect('/view-posted/expired')

    ###################################################################################################################
    #                                                Contact endpoints                                                #
    ###################################################################################################################

    # Similarly to /view-post, this method checks if the username exists. If it does, it has the render function do
    # the work.
    @route("/view-contact/<username>")
    def view_contact(self, username):
        if contact_exists_in_db(username):
            return render_template("view/contact.html", to_view=get_contact(username))
        else:
            error_message = "That username doesn't exist in the contacts database."
            return render_template("error_page.html", error=error_message)

    # Because their contact entry in the DB should be added automatically by the init_user function the first time they
    # log in to classifieds, I only made a page to edit their contact info.
    @route("/edit-contact")
    def edit_contact(self):
        return render_template("forms/contact.html", form=ContactForm(get_contact_form_data(session['username'])),
                               external=False, new=False)

    # Similarly to /submit-post, this method parses the contact form's contents, validates, and updates the DB's entry
    # for the user. If they're already in the DB, it edits their info. If an administrator is adding an external
    # contact, it adds the new information.
    @route("/submit-contact", methods=['POST'])
    def submit_contact(self):
        storage = request.form
        form = ContactForm(storage)
        is_external = (storage['external'] == 'True')
        if is_external:
            submitters_username = storage['email']
        else:
            submitters_username = session['username']
        contact_in_db = contact_exists_in_db(submitters_username)

        is_valid = form.validate()
        if not is_valid:
            return render_template("forms/contact.html", form=form, external=is_external, new=not contact_in_db)

        if is_external:
            if contact_in_db:
                edit_contact(submitters_username, storage['first_name'], storage['last_name'], storage['email'],
                             storage['phone_number'])
                message = "External contact information successfully edited!"
            else:
                add_contact(submitters_username, storage['first_name'], storage['last_name'], storage['email'],
                             storage['phone_number'])
                message = "External contact information successfully added!"
        else:
            edit_contact(submitters_username, storage['first_name'], storage['last_name'], storage['email'],
                         storage['phone_number'])
            message = "Contact information successfully updated!"
        return render_template("confirmation_page.html", message=message)

    ###################################################################################################################
    #                                                 Admin endpoints                                                 #
    ###################################################################################################################

    # This is used by administrators to submit a post to the DB that is from a person who does not have a BCA account
    @route("/add-external-post")
    def add_external_post(self):
        if contact_exists_in_db(session['username']):
            if not contact_is_admin(session['username']):
                return abort(404)
            return render_template("forms/post.html",
                                   form=ExternalPosterForm(get_post_form_data(hidden_username="")),
                                   external=True, new=True)
        else:
            error_message = "You don't exist in the contacts database yet, and as such you cannot submit a post."
            return render_template("error_page.html", error=error_message)

    @route("/edit-external-post/<post_id>")
    def edit_external_post(self, post_id):
        if contact_exists_in_db(session['username']):
            if post_exists_in_db(post_id):
                if True:  # allowed_to_edit_post(post_id, session['username']):
                    return render_template("forms/post.html", form=ExternalPosterForm(get_post_form_data(post_id)),
                                           external=True, new=False)
                else:
                    error_message = "You don't have permission to edit that post."
                    return render_template("error_page.html", error=error_message)
            else:
                error_message = "That post id number doesn't exist in the posts database."
                return render_template("error_page.html", error=error_message)
        else:
            error_message = "You don't exist in the contacts database yet, and as such you cannot edit a post."
            return render_template("error_page.html", error=error_message)

    # Asks the administrator to confirm that they want to delete a specific post
    @route("/delete-post-confirm/<post_id>")
    def delete_post_confirm(self, post_id):
        if not contact_is_admin(session['username']):
            return abort(404)
        return render_template('admin/delete_post_confirm.html', post=get_post(post_id))

    # Allows administrators to delete posts that do not comply with BU standards
    @route("/delete-post/<post_id>")
    def delete_post(self, post_id):
        if not contact_is_admin(session['username']):
            return abort(404)

        delete_post(post_id)

        return redirect('/')

    # For administrators to add people who do not have a BCA account to the DB so that people who click on their posts
    # can contact them, instead of the admins.
    @route("/add-external-contact")
    def add_external_contact(self):
        if contact_is_admin(session['username']):
            return render_template("forms/contact.html", form=ContactForm(), external=True, new=True)
        else:
            return abort(404)

    @route("/edit-external-contact/<email>")
    def edit_external_contact(self, email):
        if contact_is_admin(session['username']):
            return render_template("forms/contact.html", form=ContactForm(get_contact_form_data(email)),
                                   external=True, new=False)
        else:
            return abort(404)

    # For administrators to add a new category that everyone can choose from in their submissions
    @route("/add-category")
    def add_new_category(self):
        if contact_exists_in_db(session['username']):
            if not contact_is_admin(session['username']):
                return abort(404)
            return render_template("forms/category.html", form=CategoryForm(get_category_form_data()), new=True)
        else:
            error_message = "You don't exist in the contacts database yet, and as such you cannot add a category."
            return render_template("error_page.html", error=error_message)

    @route("/manage-categories")
    def manage_categories(self):
        if not contact_is_admin(session['username']):
            return abort(404)
        return render_template("admin/manage_categories.html", categories=get_category_list())

    @route("/edit-category/<category_id>")
    def edit_category(self, category_id):
        if contact_exists_in_db(session['username']):
            if not contact_is_admin(session['username']):
                return abort(404)
            return render_template("forms/category.html", form=CategoryForm(get_category_form_data(category_id)), new=False)
        else:
            error_message = "You don't exist in the contacts database yet, and as such you cannot edit a category."
            return render_template("error_page.html", error=error_message)

    @route("/delete-category-confirm/<category_id>")
    def delete_category_confirm(self, category_id):
        if not contact_is_admin(session['username']):
            return abort(404)
        return render_template('admin/delete_category_confirm.html', category=get_category(category_id))

    @route("/delete-category/<category_id>")
    def delete_category(self, category_id):
        if not contact_is_admin(session['username']):
            return abort(404)

        delete_category(category_id)

        return redirect('/')

    # The corresponding post method to /add-category
    @route("/submit-category", methods=['POST'])
    def submit_category(self):
        storage = request.form
        form = CategoryForm(storage)
        is_valid = form.validate()
        is_new = int(storage['id']) < 0
        if not is_valid:
            return render_template("forms/category.html", form=form, new=is_new)
        if is_new:  # Adding a new category
            result = add_category(storage['category_html'], storage['category_human'])
            if result:
                message = "Category successfully added!"
            else:
                message = "Category failed to be added; please try again."
        else:  # Editing an existing category
            result = edit_category(storage['id'], storage['category_html'], storage['category_human'])
            if result:
                message = "Category successfully edited!"
            else:
                message = "Category failed to be edited; please try again."
        if result:
            return render_template("confirmation_page.html", message=message)
        else:
            return render_template("error_page.html", error=message)

    # Used by administrators to manage the privilege levels of people who are not them. Any admin can promote any
    # non-admin to admin level, and any admin can demote any admin except themselves. This way, there is ALWAYS at least
    # one administrator.
    @route("/manage-privileges")
    def manage_privileges(self):
        # TODO: I'd like to make the table in this form sortable, like the main page.
        if not contact_is_admin(session['username']):
            return abort(404)
        else:
            return render_template("admin/user_permissions_form.html", non_admins=get_non_admins(), admins=get_admins())

    # Used to promote a group of non-admins to admin level
    @route("/group-promote", methods=['POST'])
    def group_promote(self):
        if contact_is_admin(session['username']):
            storage = request.form
            for key in storage:
                make_admin(storage[key])
            return redirect('/manage-privileges')
        else:
            return abort(404)

    # Used to promote a single non-admin to admin level using their username
    @route("/single-promote", methods=['POST'])
    def single_promote(self):
        if contact_is_admin(session['username']):
            storage = request.form
            make_admin(storage['promotee'])
            return redirect('/manage-privileges')
        else:
            return abort(404)

    # Used to demote a group of admins down to non-admin level
    @route("/group-demote", methods=['POST'])
    def group_demote(self):
        if contact_is_admin(session['username']):
            storage = request.form
            for key in storage:
                remove_admin(storage[key])
            return redirect('/manage-privileges')
        else:
            return abort(404)

    ###################################################################################################################
    #                                                  Utility endpoints                                              #
    ###################################################################################################################

    def faq(self):
        return render_template(app.config['FAQ_PAGE'])

    # This method is to be used by the crontab job; it should be called every night at midnight, and mark all posts that
    # expired during that day as expired.
    def expire(self):
        expire_old_posts()
        return "Old posts expired"

    # This method is simply to allow them to sign out of CAS Auth as well as the classifieds site itself.
    def logout(self):
        return redirect("https://auth.bethel.edu/cas/logout")

    # These last two methods are designed to be here only temporarily. They allow the users to submit feedback about the
    # site, whether it's a feature suggestion or bugfix.
    def feedback(self):
        return render_template("feedback.html")

    # Arbitrary comment
    @route("/submit-feedback", methods=['POST'])
    def submit_feedback(self):
        print request.form
        send_feedback_email(request.form, session['username'])
        message = "Thank you for submitting feedback! We'll take a look at your message and try to make the " \
                  "site better for everyone!"
        return render_template("confirmation_page.html", message=message)
