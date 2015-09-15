__author__ = 'phg49389'

from flask import Flask
from classifieds.views import ClassifiedsView
from forms import create_ads_table, table_exists, create_contacts_table  # , contacts_table_exists

if __name__ == '__main__':
    if not table_exists("classifieds"):
        create_ads_table()
    if not table_exists("contacts"):
        create_contacts_table()
    app = Flask(__name__)
    ClassifiedsView.register(app)
    app.run(debug=True)
