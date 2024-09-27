from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional, Regexp

# form when logging in to sharecipe
class LoginForm(FlaskForm):
    email = EmailField('Email', [
        InputRequired(message='Email is required'),
        Email(message='Enter a valid email address')
        ], description='Enter your email')
    password = PasswordField('Password', [
        InputRequired(message='Password is required')
        ], description='Enter your password')
    #next = HiddenField(default='main.index')

# form when signing up to sharecipe
class RegisterForm(FlaskForm):
    email = EmailField('Email', [
        InputRequired(message='Email address is required'),
        Email(message='Enter a valid email address'),
        Length(max=256, message='Email must not be more than 256 characters'),
        ], description='Enter your email address to help recover your account if lost')
    name = StringField('Name', [
        InputRequired(message='Name is required'),
        Length(max=56,
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

class VerifyForm(FlaskForm):
    code = StringField('Code', [
        InputRequired(message='Code is required'),
    ], description='Enter your verification code')
