from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional, Regexp

# form when logging in to sharecipe
class LoginForm(FlaskForm):
    username = StringField('Username', [
        InputRequired(message='Username is required')
        ], description='Enter your username')
    password = PasswordField('Password', [
        InputRequired(message='Password is required')
        ], description='Enter your password')
    #next = HiddenField(default='main.index')

# form when signing up to sharecipe
class RegisterForm(FlaskForm):
    username = StringField('Username', [
        InputRequired(message='Username is required'),
        Length(min=3, max=36, message='Username must be between 3 and 36 characters'),
        Regexp('^[a-zA-Z0-9-_.]*$', message='Username can only consist of upper and lower case letters, numbers, hyphens, underscores and periods'),
        ], description='Choose a unique username to identify your account')
    email = EmailField('Email', [
        InputRequired(message='Email address is required'),
        Email(message='Enter a valid email address'),
        Length(max=256, message='Email must not be more than 256 characters'),
        ], description='Enter your email address to help recover your account if lost')
    name = StringField('Name', [
        Optional(), Length(max=56,
            message='Name must not exceed 56 characters')
        ], description='This is how you\'ll be known')
    password = PasswordField('Password', [
        InputRequired(message='Password is required'),
        Length(min=8, max=256, message='Password must be between 8 and 256 characters')
        ], description='Choose a strong password to protect your account')
    confirm_password = PasswordField('Confirm Password', [
        InputRequired(message='Password confirmation is required'),
        EqualTo('password', message='Passwords must match')
        ], description='Confirm your password')
