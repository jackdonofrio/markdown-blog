from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from flask_mde import MdeField
from markdown_blog.models import User

class MdeForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    editor = MdeField(validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
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
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email in use; please log in or choose a different one')


class UpdateAccountForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Length(max=100)])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('Email in use; please log in or choose a different one')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')