__author__ = 'phg49389'

from flask import request, render_template
from flask.ext.classy import FlaskView, route
from classifieds.forms import get_classified_form, get_contact_form, get_homepage, \
    submit_classified_form, submit_contact_form, view_classified, get_contact, filter_posts, \
    query_database
from db_utilities import mark_entry_as_complete, mark_entry_as_active


class View(FlaskView):

    def index(self):
        return render_template("homepage.html", values=get_homepage())

    def addClassified(self):
        return render_template("classifiedForm.html", form=get_classified_form())

    def addContact(self):
        return render_template("contactForm.html", form=get_contact_form(), info=[])

    def editContact(self, username):
        return render_template("contactForm.html", form=get_contact_form(), info=get_contact(username))

    @route("/submitAd", methods=['POST'])
    def submit_ad(self):
        # TODO: need to figure out a way to pass sign-in to this method
        return render_template("submissionResults.html", result=submit_classified_form(request.form, "enttes"))

    @route("/submitContact", methods=['POST'])
    def submit_contact(self):
        return render_template("submissionResults.html", result=submit_contact_form(request.form))

    def viewClassified(self, id):
        return render_template("viewClassified.html", classified=view_classified(id))

    def viewContact(self, username):
        return render_template("viewContact.html", contact=get_contact(username))

    def viewPosted(self, selector):
        return render_template("viewUsersPosts.html", posts=filter_posts("enttes", selector))

    def searchPage(self):
        return render_template("searchPage.html")

    @route("/search", methods=['POST'])
    def search(self):
        # Turn the lists into strings
        storage = dict(request.form)
        to_send = {}
        for key in storage:
            if isinstance(storage[key], list):
                if len(storage[key]) > 1:  # Means that multiple categories are being selected
                    to_send[key] = storage[key]
                else:
                    storage[key] = storage[key][0]
                    if storage[key] != '':
                        to_send[key] = u'%' + storage[key] + u'%'
        return render_template("searchResults.html", results=query_database(to_send))

    def markComplete(self, id):
        mark_entry_as_complete(id)
        return render_template("homepage.html", values=get_homepage())

    def reactivate(self, id):
        mark_entry_as_active(id)
        return render_template("homepage.html", values=get_homepage())
