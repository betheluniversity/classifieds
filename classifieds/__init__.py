__author__ = 'phg49389'

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from classifieds.views import View
View.register(app)


# from flask import current_app, request, session
# if current_app.config['ENVIRON'] == 'prod':
#     username = request.environ.get('REMOTE_USER')
# else:
#     username = current_app.config['TEST_USER']
# session['username'] = username
