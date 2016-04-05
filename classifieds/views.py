from classifieds.forms import get_homepage, view_classified, filter_posts, query_database, \
    send_feedback_email, ClassifiedForm, ContactForm
from db_utilities import *
from flask import request, render_template, session, redirect
from flask.ext.classy import FlaskView, route


# This Flask-Classy object is simply named "View" because Flask-Classy takes whatever is in front of View and makes it
# the first argument of the url, such that "ClassifiedsView" would be accessed via classifieds.bethel.edu/classifieds
# To avoid that, I put nothing in front of "View" so now all the URLs will have the form classifieds.bethel.edu/url-name
class View(FlaskView):

    # This method doesn't need the actual word index; just the base URL will work to return the homepage
    def index(self):
        return render_template("homepage.html", values=get_homepage(), showStatus=False)

    # This URL is only for rendering to a channel in BLink
    @route("/blink-classifieds")
    def blink_classifieds(self):
        return render_template("blinkTemplate.html", values=get_homepage(), showStatus=False)

    # This URL is to get the classified ad form so that the user can fill it out and submit it to the DB
    @route("/add-classified")
    def add_classified(self):
        if contact_exists_in_db(session['username']):
            return render_template("classifiedForm.html", form=ClassifiedForm())
        else:
            error_message = "You don't exist in the contacts database yet, and as such you cannot submit a classified."
            return render_template("errorPage.html", error=error_message)

    # Because their contact entry in the DB should be added automatically by the init_user function the first time they
    # log in to classifieds, I only made a page to edit their contact info.
    @route("/edit-contact")
    def edit_contact(self):
        return render_template("contactForm.html", form=ContactForm(), info=get_contact(session['username']))

    # This is a post method that takes the classified form's contents, parses them, validates, and if it passes, it adds
    # it to the DB and then returns to the page if it was successful or not.
    @route("/submit-ad", methods=['POST'])
    def submit_ad(self):
        form_contents = request.form
        form = ClassifiedForm(form_contents)
        isValid = form.validate()
        if not isValid:
            return render_template("classifiedForm.html", form=form)
        storage = {}
        for key in form_contents:
            if key == "submit":
                continue
            raw_values = form_contents.getlist(key)
            if len(raw_values) > 1:
                parsed_values = ""
                for val in raw_values:
                    parsed_values += val + ";"
                parsed_values = parsed_values[:-1]  # Remove last semicolon; unnecessary
            else:
                parsed_values = raw_values[0]
            storage[key] = parsed_values
        # Add that object to the database
        add_classified(storage['title'], storage['description'], storage['price'], storage['categories'], session['username'])
        message = "Classified ad successfully posted!"
        return render_template("confirmationPage.html", message=message)

    # Similarly to submit_ad, this method parses the contact form's contents, validates, and updates the DB's entry for
    # the user.
    @route("/submit-contact", methods=['POST'])
    def submit_contact(self):
        storage = request.form
        form = ContactForm(storage)
        isValid = form.validate()
        if not isValid:
            return render_template("contactForm.html", form=form)
        # Add that object to the database
        add_contact(session['username'], storage['first_name'], storage['last_name'], storage['email'], storage['phone_number'])
        message = "Contact information successfully updated!"
        return render_template("confirmationPage.html", message=message)

    # This method is pretty straightforward, just checks if the id they're requesting exists. If it does, it renders it.
    # The render itself takes care of the ad's expired/completed status, if it's the original poster, etc.
    @route("/view-classified/<id>")
    def view_classified(self, id):
        if classified_exists_in_db(id):
            return render_template("viewClassified.html", classified=view_classified(id))
        else:
            error_message = "That classified id number doesn't exist in the contacts database."
            return render_template("errorPage.html", error=error_message)

    # Similarly to viewClassified, this method checks if the username exists. If it does, it has the render function do
    # the work.
    @route("/view-contact/<username>")
    def view_contact(self, username):
        if contact_exists_in_db(username):
            return render_template("viewContact.html", to_view=get_contact(username))
        else:
            error_message = "That username doesn't exist in the contacts database."
            return render_template("errorPage.html", error=error_message)

    # This method is more or less a 'hub' for all the various ways that a poster would like to view the posts that
    # they've made. This passes on what type of posts they want to see, the DB does the filtering and returns the list,
    # and they all get rendered the same way.
    @route("/view-posted/<selector>")
    def view_posted(self, selector):
        if contact_exists_in_db(session['username']):
            return render_template("viewUsersPosts.html", posts=filter_posts(session['username'], selector))
        else:
            error_message = "You don't exist in the contacts database yet, and as such you don't have any posts to view."
            return render_template("errorPage.html", error=error_message)

    # Really straightforward method, simply renders the search page.
    @route("/search-page")
    def search_page(self):
        return render_template("searchPage.html")

    # This method does a bit of work in preparation of the DB query; it creates a dictionary of search terms that are
    # keyed to match the keyword arguments of the DB search method in forms. If they're searching for a single word,
    # that word is bounded by the DB's wildcard character, '%'. If there are multiple search terms, it splits it into a
    # list that gets dealt with by the DB's search method.
    @route("/search", methods=['POST'])
    def search(self):
        storage = dict(request.form)
        storage['title'] = storage['title'][0].split(" ")
        storage['description'] = storage['description'][0].split(" ")
        to_send = {}
        for key in storage:
            if len(storage[key]) == 1:
                if len(storage[key][0]) > 0:
                    to_send[key] = u'%' + storage[key][0] + u'%'
            else:
                to_send[key] = storage[key]
        to_send['expired'] = False
        to_send['completed'] = False
        return render_template("homepage.html", values=query_database(to_send), showStatus=True)

    # A pretty straightforward pair of methods; if the poster calls this URL via a link on the pages, it will change
    # that value appropriately in the DB.
    @route("/mark-complete/<id>")
    def mark_complete(self, id):
        mark_entry_as_complete(id, session['username'])
        return redirect('/view-posted/active')

    def reactivate(self, id):
        mark_entry_as_active(id, session['username'])
        return redirect('/view-posted/expired')

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

    #
    @route("/submit-feedback", methods=['POST'])
    def submit_feedback(self):
        send_feedback_email(request.form, session['username'])
        message = "Thank you for submitting feedback! We'll take a look at your message and try to make the " \
                  "site better for everyone!"
        return render_template("confirmationPage.html", message=message)
