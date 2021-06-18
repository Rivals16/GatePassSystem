from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     BooleanField, TextAreaField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.validators import ValidationError
from minor.models import User


class RegistrationForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(
                            min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                    EqualTo('password')])
    signup = SubmitField('Sign up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email Alreay Exist!', 'danger')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    login = SubmitField('Login')


class ResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(
                            min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                    EqualTo('password')])
    submit = SubmitField('Change password')


class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')
