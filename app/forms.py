# Standard library imports
import re

# Third party imports
from flask import render_template
from wtforms import Form, HiddenField, SelectMultipleField, StringField
from wtforms import SubmitField, TextAreaField, ValidationError, validators

# Local application imports
from controller import get_category_list


# This is a custom validator that I made to make sure that they put in valid phone numbers into their Contact form
def phone_validator():
    message = 'Must have a valid phone number'

    def _phone(form, field):
        phone_pattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')
        result = phone_pattern.search(field.data)
        if result is None:
            raise ValidationError(message)

    return _phone


# This is a custom validator that I made to make sure that any emails put in will only use characters that are also safe
# to call in URLs, like app.bethel.edu/view-contact/example@fake.com
def safe_for_url():
    message = 'The text provided would not work in a URL bar'

    def _safe(form, field):
        bad_chars = re.compile(r'(["%<> /\\{|}\^]+)')
        result = bad_chars.search(field.data)
        if result:
            raise ValidationError(message)

    return _safe


class RenderableForm(Form):

    def render_to_html(self):
        return render_template('forms/generic.html', fields=self._fields.iteritems())


# WTForm objects that are used in rendering. Each Field in this object corresponds to the user-input columns in the DB
class RegularPostForm(RenderableForm):
    post_id = HiddenField('', [validators.DataRequired(), validators.Length(max=8)])
    submitters_username = HiddenField('', [validators.DataRequired(), validators.Length(max=50)])
    title = StringField('Title:', [validators.DataRequired(), validators.Length(max=100)])
    description = TextAreaField('Description:', [validators.DataRequired(), validators.Length(max=1000)])
    price = StringField('Price:', [validators.DataRequired(), validators.Length(max=50)])
    categories = SelectMultipleField('Categories:', [validators.DataRequired()],
                                     choices=get_category_list(return_list_of_tuples=True))
    submit = SubmitField('Submit')


class ExternalPosterForm(RenderableForm):
    post_id = HiddenField('', [validators.DataRequired(), validators.Length(max=8)])
    submitters_username = StringField('Email of external poster:', [validators.DataRequired(),
                                                                    validators.Length(max=50)])
    title = StringField('Title:', [validators.DataRequired(), validators.Length(max=100)])
    description = TextAreaField('Description:', [validators.DataRequired(), validators.Length(max=1000)])
    price = StringField('Price:', [validators.DataRequired(), validators.Length(max=50)])
    categories = SelectMultipleField('Categories:', [validators.DataRequired()],
                                     choices=get_category_list(return_list_of_tuples=True))
    submit = SubmitField('Submit')


class ContactForm(RenderableForm):
    first_name = StringField('First Name:', [validators.DataRequired(), validators.Length(max=20)])
    last_name = StringField('Last Name:', [validators.DataRequired(), validators.Length(max=30)])
    email = StringField('Email address:', [validators.DataRequired(), validators.Email(), safe_for_url()])
    phone_number = StringField('Phone Number:', [validators.DataRequired(), phone_validator()])
    submit = SubmitField('Submit')


class CategoryForm(RenderableForm):
    category_id = HiddenField('', [validators.DataRequired(), validators.Length(max=8)])
    category_html = StringField('HTML version of the category:', [validators.DataRequired(), validators.Length(max=50)])
    category_human = StringField('Human-friendly version of the category:', [validators.DataRequired(), validators.Length(max=50)])
    submit = SubmitField('Submit')
