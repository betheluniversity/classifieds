__author__ = 'phg49389'

from flask import request, render_template, session
from flask.ext.classy import FlaskView, route
from classifieds.forms import get_classified_form, get_contact_form, get_homepage, \
    submit_classified_form, submit_contact_form, view_classified, get_contact, filter_posts, \
    query_database
from db_utilities import mark_entry_as_complete, mark_entry_as_active, expire_old_posts, contact_exists_in_db


class View(FlaskView):

    def index(self):
        return render_template("homepage.html", values=get_homepage())

    def addClassified(self):
        if contact_exists_in_db(session['username']):
            return render_template("classifiedForm.html", form=get_classified_form())
        else:
            return render_template("contactForm.html", form=get_contact_form(), info=[])

    def editContact(self):
        return render_template("contactForm.html", form=get_contact_form(), info=get_contact(session['username']))

    @route("/submitAd", methods=['POST'])
    def submit_ad(self):
        return render_template("submissionResults.html", result=submit_classified_form(request.form, session['username']))

    @route("/submitContact", methods=['POST'])
    def submit_contact(self):
        return render_template("submissionResults.html", result=submit_contact_form(request.form))

    def viewClassified(self, id):
        return render_template("viewClassified.html", classified=view_classified(id))

    def viewContact(self, username):
        if contact_exists_in_db(username):
            return render_template("viewContact.html", to_view=get_contact(username))
        else:
            return render_template("contactForm.html", form=get_contact_form(), info=[])

    def viewPosted(self, selector):
        if contact_exists_in_db(session['username']):
            return render_template("viewUsersPosts.html", posts=filter_posts(session['username'], selector))
        else:
            return render_template("contactForm.html", form=get_contact_form(), info=[])

    def searchPage(self):
        return render_template("searchPage.html")

    @route("/search", methods=['POST'])
    def search(self):
        storage = dict(request.form)
        storage['title'] = storage['title'][0].split(" ")
        storage['description'] = storage['description'][0].split(" ")
        to_send = {}
        for key in storage:
            # print storage[key]
            if len(storage[key]) == 1:
                if len(storage[key][0]) > 0:
                    # print "storage[key] is '" + storage[key][0] + "'"
                    to_send[key] = u'%' + storage[key][0] + u'%'
            else:
                to_send[key] = storage[key]
        to_send['expired'] = False
        to_send['completed'] = False
        # print to_send
        return render_template("searchResults.html", results=query_database(to_send))

    def markComplete(self, id):
        mark_entry_as_complete(id)
        return render_template("homepage.html", values=get_homepage())

    def reactivate(self, id):
        mark_entry_as_active(id)
        return render_template("homepage.html", values=get_homepage())

    def expire(self):
        expire_old_posts()
        return "Old posts expired"
