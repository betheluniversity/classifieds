__author__ = 'phg49389'

from flask import request, render_template
from flask.ext.classy import FlaskView, route
from classifieds.forms import get_classified_form, get_contact_form, get_homepage, submit_classified_form, submit_contact_form


class View(FlaskView):

    def index(self):
        return render_template("homepage.html", values=get_homepage())

    def addClassified(self):
        return render_template("classifiedForm.html", form=get_classified_form())

    def addContact(self):
        return render_template("contactForm.html", form=get_contact_form())

    @route("/submitAd", methods=['POST'])
    def submit_ad(self):
        return submit_classified_form(request.form, "phg49389")

    @route("/submitContact", methods=['POST'])
    def submit_contact(self):
        return submit_contact_form(request.form)
