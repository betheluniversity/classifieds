__author__ = 'phg49389'

from flask import request, render_template, session, redirect
from flask.ext.classy import FlaskView, route
from classifieds.forms import get_homepage, view_classified, filter_posts, query_database, \
    send_feedback_email, ClassifiedForm, ContactForm
from db_utilities import *


class View(FlaskView):

    def index(self):
        return render_template("homepage.html", values=get_homepage())

    def addClassified(self):
        if contact_exists_in_db(session['username']):
            return render_template("classifiedForm.html", form=ClassifiedForm())
        else:
            error_message = "You don't exist in the contacts database yet, and as such you cannot submit a classified."
            return render_template("errorPage.html", error=error_message)

    def editContact(self):
        return render_template("contactForm.html", form=ContactForm(), info=get_contact(session['username']))

    @route("/submitAd", methods=['POST'])
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

    @route("/submitContact", methods=['POST'])
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

    def viewClassified(self, id):
        return render_template("viewClassified.html", classified=view_classified(id))

    def viewContact(self, username):
        if contact_exists_in_db(username):
            return render_template("viewContact.html", to_view=get_contact(username))
        else:
            error_message = "That username doesn't exist in the contacts database."
            return render_template("errorPage.html", error=error_message)

    def viewPosted(self, selector):
        if contact_exists_in_db(session['username']):
            return render_template("viewUsersPosts.html", posts=filter_posts(session['username'], selector))
        else:
            error_message = "You don't exist in the contacts database yet, and as such you don't have any posts to view."
            return render_template("errorPage.html", error=error_message)

    def searchPage(self):
        return render_template("searchPage.html")

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
        return render_template("homepage.html", values=query_database(to_send))

    def markComplete(self, id):
        mark_entry_as_complete(id, session['username'])
        return redirect('/viewPosted/active')

    def reactivate(self, id):
        mark_entry_as_active(id, session['username'])
        return redirect('/viewPosted/expired')

    def logout(self):
        return redirect("https://auth.bethel.edu/cas/logout")

    def expire(self):
        expire_old_posts()
        return "Old posts expired"

    def feedback(self):
        return render_template("feedback.html")

    @route("/submitFeedback", methods=['POST'])
    def submit_feedback(self):
        send_feedback_email(request.form, session['username'])
        message = "Thank you for submitting feedback! We'll take a look at your message and try to make the " \
                  "site better for everyone!"
        return render_template("confirmationPage.html", message=message)
