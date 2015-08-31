__author__ = 'phg49389'

from flask import Flask
from primary_directory.view import ClassifiedsView

if __name__ == '__main__':
    app = Flask(__name__)
    ClassifiedsView.register(app)
    app.run(debug=True)
