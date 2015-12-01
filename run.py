__author__ = 'phg49389'

from classifieds import app
from classifieds.views import View

if __name__ == '__main__':
    View.register(app)
    app.run(debug=True)
