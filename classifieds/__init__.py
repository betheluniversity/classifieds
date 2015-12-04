__author__ = 'phg49389'

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# from migrate.versioning import api
# from config import SQLALCHEMY_DATABASE_URI
# from config import SQLALCHEMY_MIGRATE_REPO
# import os.path

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# print db.get_tables_for_bind()
# if len(db.get_tables_for_bind()) < 1:
#     from models import Classifieds, Contacts
#     db.create_all()
#     if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
#         api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
#         api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
#     else:
#         api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
#     db.session.commit()
# print db.get_tables_for_bind()
