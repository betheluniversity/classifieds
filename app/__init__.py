# Standard library imports
import ast
import requests

# Third party imports
from flask import current_app, Flask, request, session, make_response, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

if app.config['SENTRY_URL']:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    sentry_sdk.init(dsn=app.config['SENTRY_URL'], integrations=[FlaskIntegration()])

# Local application imports
# These imports need to be after app and db's creation, as they get imported into views.py, from which this imports.
from app.models import Contacts
from app.views import View
from app.controller import contact_is_admin, get_app_settings
View.register(app)


@app.before_request
def before_request():
    try:
        init_user()
    except:
        app.logger.info('failed to init')


# This method sees who's logging in to the website, and then checks if they're in the contacts DB. If they are, it grabs
# their info from the DB for rendering. If not, then it creates a default entry for that user using info from wsapi.
def init_user():
    if current_app.config['ENVIRON'] == 'prod':
        username = request.environ.get('REMOTE_USER')
    else:
        username = current_app.config['TEST_USER']
    session['username'] = username
    contact = Contacts.query.filter(Contacts.username.like(username)).first()
    if contact is not None:
        session['fullname'] = contact.first_name + ' ' + contact.last_name
    else:
        banner_info = requests.get('https://wsapi.bethel.edu/username/' + username + '/names')
        info_dict = ast.literal_eval(banner_info.text)['0']
        primary_name = info_dict['firstName']
        if len(info_dict['prefFirstName']) > 0:
            primary_name = info_dict['prefFirstName']
        session['fullname'] = primary_name + ' ' + info_dict['lastName']
        new_contact = Contacts(username=username, first=primary_name, last=info_dict['lastName'],
                               email=username + '@bethel.edu', phone='')
        db.session.add(new_contact)
        db.session.commit()


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    resp = make_response(redirect(app.config['LOGOUT_URL']))
    resp.set_cookie('MOD_AUTH_CAS_S', '', expires=0)
    resp.set_cookie('MOD_AUTH_CAS', '', expires=0)
    return resp


def is_user_admin():
    return True
    # return contact_is_admin(session['username'])


@app.context_processor
def utility_processor():
    to_return = {}

    to_return.update({
        "is_user_admin": is_user_admin,
        "app_settings": get_app_settings()})

    # you have to update before you can return the context_processor
    return to_return
