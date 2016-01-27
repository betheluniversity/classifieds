__author__ = 'phg49389'

from classifieds import app
import os

if __name__ == '__main__':
    print os.path.dirname(os.path.realpath(__file__))
    app.run(debug=True)
