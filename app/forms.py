#python module that contains the different forms that might be needed


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User


# Form that will be fed into the login.html page
class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # adding a password confirmation check
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]
    )

    submit = SubmitField('Register')


    # adding custom validation for username, to check that it has not already been registered.
    # the below validators in forms.py will provide individual field validation, so the user knows why the registration failed.
    # Notice that for login function, the validation happens in the routes.py as a flash message. This was just done differently, as the user does not need individual field validation there
    # When you add any methods that match the pattern validate_<field_name> (.e.g 'validate_username'),
    # WTForms takes those as custom validators and invokes them in addition to the stock validators.
    # When a validation error is triggered, the message included as the argument in the exception will be the message that
    # will be displayed next to the field for the user to see.
    def validate_username(self, username):
        # Note that the queries use db.session.scalar(), which returns none if there are no results, or returns the first result if there is 1 or more
        # db.session.scalars() --> with an 's' at the end, would return multiple entries if more than 1 exists.
        # For this example, we don't care if there is more than 1 match. We only care if there is a match or not
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username')

    # creating another customer validator with WTForms,
    # this time to validate that the email submitted for registration
    # has not already been taken by another user in the database
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address')
        
