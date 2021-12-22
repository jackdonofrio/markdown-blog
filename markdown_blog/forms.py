"""
this module contains the input forms used
in this web app
"""

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from flask_mde import MdeField
from markdown_blog.models import User

class MdeForm(FlaskForm):
    """ Markdown editor fields """

    title = StringField("Title", validators=[DataRequired()])
    editor = MdeField(validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegistrationForm(FlaskForm):
    """ Fields for registering an account """

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password',
                                      validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """
        validates whether a username is acceptable,
        based on whether it is available and is
        strictly alphanumeric
        """
        # first check if it's taken
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username exists; please choose a different one.')
        # then check if it's alphanumeric
        if not username.data.isalnum():
            raise ValidationError("Usernames must be alphanumeric.")


    # careful with emails; this can be a security flaw allowing users to figure our
    # registered emails which are normally hidden from other users

    def validate_email(self, email):
        """ checks whether email is available """

        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email in use; please log in or choose a different one')


class UpdateAccountForm(FlaskForm):
    """ fields for updating user account info """

    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Length(max=100)])
    submit = SubmitField('Update')

    def validate_email(self, email):
        """ checks whether email is available """

        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('Email in use; please log in or choose a different one')

class LoginForm(FlaskForm):
    """ fields for logging into an account"""

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
