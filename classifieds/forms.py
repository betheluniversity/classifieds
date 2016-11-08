import re
from controller import get_category_list
from wtforms import Form, StringField, SelectMultipleField, TextAreaField, SubmitField, validators, ValidationError

# This is a custom validator that I made to make sure that they put in valid phone numbers into their Contact form
def phone_validator():
    message = 'Must have a valid phone number'

    def _phone(form, field):
        phone_pattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')
        result = phone_pattern.search(field.data)
        if result is None:
            raise ValidationError(message)

    return _phone


# 3 WTForm objects that are used in rendering. Each Field in this object corresponds to the user-input columns in the DB
class PostForm(Form):
    title = StringField('Title:', [validators.DataRequired(), validators.Length(max=100)])
    description = TextAreaField('Description:', [validators.DataRequired(), validators.Length(max=1000)])
    price = StringField('Price:', [validators.DataRequired(), validators.Length(max=50)])
    categories = SelectMultipleField('Categories:', [validators.DataRequired()],
                                     choices=get_category_list(return_list_of_tuples=True))
    submit = SubmitField("Submit")


class ContactForm(Form):
    first_name = StringField('First Name:', [validators.DataRequired(), validators.Length(max=20)])
    last_name = StringField('Last Name:', [validators.DataRequired(), validators.Length(max=30)])
    email = StringField('Email address:', [validators.DataRequired(), validators.Email()])
    phone_number = StringField('Phone Number:', [validators.DataRequired(), phone_validator()])
    submit = SubmitField("Update")


class CategoryForm(Form):
    category_html = StringField('HTML version of the category:', [validators.DataRequired(), validators.Length(max=50)])
    category_human = StringField('Human-friendly version of the category:', [validators.DataRequired(), validators.Length(max=50)])
    submit = SubmitField("Submit")

