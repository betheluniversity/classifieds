__author__ = 'phg49389'

from wtforms import Form, StringField, SelectMultipleField, TextAreaField, FormField, SubmitField


# Returns the WTForm version of the form to be made into HTML
def get_form():
    return ClassifiedForm()


class ContactInfoForm(Form):
    name = StringField('Name:')
    email = StringField('Email:')
    phone_number = StringField('Phone number:')


class ContentForm(Form):
    title = StringField('Title:')
    description = TextAreaField('Description:')
    categories = SelectMultipleField('Categories:')


class ClassifiedForm(Form):
    # name = StringField('Name:')
    # email = StringField('Email:')
    # phone_number = StringField('Phone number:')
    # title = StringField('Title:')
    # description = TextAreaField('Description:')
    # categories = SelectMultipleField('Categories:')
    contact_info = FormField(ContactInfoForm)
    content = FormField(ContentForm)
    submit = SubmitField("Submit")


# Returns whether or not it was successfully submitted
def submit_form(form_contents):
    # Flat array of 6 values as argument
    # Turn them into a SQLite object
    # Add that object to the database and store the result
    result = False
    if result:
        return """
        <html>
            <head>
                <title>Success</title>
            </head>
            <body>
                Classified successfully submitted!
            </body>
        </html>
        """
    else:
        return """
        <html>
            <head>
                <title>Failure</title>
            </head>
            <body>
                Classified was not successfully submitted.
            </body>
        </html>
        """
