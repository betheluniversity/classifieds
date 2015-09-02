__author__ = 'phg49389'

import json
from flask import request, render_template
from flask.ext.classy import FlaskView, route
from classifieds.forms import get_form, submit_form

class ClassifiedsView(FlaskView):

    def index(self):
        return render_template("classifiedForm.html", form=get_form())

    @route("/submit", methods=['POST'])
    def submit(self):
        form_data = json.loads(request.form['data'])
        return submit_form(form_data)
