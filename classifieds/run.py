__author__ = 'phg49389'

from flask import Flask
from classifieds.views import View
from forms import create_classifieds_table, table_exists, create_contacts_table

if __name__ == '__main__':
    if not table_exists("classifieds"):
        create_classifieds_table()
    if not table_exists("contacts"):
        create_contacts_table()
    app = Flask(__name__)
    View.register(app)
    app.run(debug=True)
