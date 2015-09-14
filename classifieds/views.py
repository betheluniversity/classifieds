__author__ = 'phg49389'

from flask import request, render_template
from flask.ext.classy import FlaskView, route
from classifieds.forms import get_form, submit_form

class ClassifiedsView(FlaskView):

    def index(self):
        return render_template("classifiedForm.html", form=get_form())

    @route("/submitAd", methods=['POST'])
    def submit_ad(self):
        return submit_form(request.form, "phg49389")
