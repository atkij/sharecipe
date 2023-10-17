from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import BooleanField, EmailField, Field, IntegerField, MultipleFileField, PasswordField, RadioField, SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import Email, EqualTo, InputRequired, Length, NumberRange, Optional, ValidationError
from wtforms.widgets import TextInput

from PIL import Image

from flask import g

from sharecipe.util import check_password_hash

# additional validator for checking when one field is not equal to another
class NotEqualTo(object):
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError as exc:
            raise ValidationError(
                    field.gettext('Invalid field name \'%s\'.') % self.fieldname
                    ) from exc

        if field.data != other.data:
            return

        d = {
                'other_label': hasattr(other , 'label')
                and other.label.text
                or self.fieldname,
                'other_name': self.fieldname,
                }

        message = self.message
        if message is None:
            message = field.gettext('Field must not be equal to %(other_name)s.')

        raise ValidationError(message % d)

# validator check if password is correct for already signed in user
class PasswordCheck(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if g.user is not None and check_password_hash(g.user['password'], field.data):
            return

        message = self.message
        if message is None:
            message = 'Password incorrect'

        raise ValidationError(message)

# form when logging in to sharecipe
class LoginForm(FlaskForm):
    username = StringField('Username', [
        InputRequired(message='Username is required')
        ], description='Enter your username')
    password = PasswordField('Password', [
        InputRequired(message='Password is required')
        ], description='Enter your password')

# form when signing up to sharecipe
class RegisterForm(FlaskForm):
    username = StringField('Username', [
        InputRequired(message='Username is required'),
        Length(min=3, max=36, message='Username must be between 3 and 36 characters')
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

# form for updating profile
class UpdateProfileForm(FlaskForm):
    name = StringField('Name', [
        Optional(),
        Length(max=56, message='Your name cannot be more than 56 characters')
        ], description='This is how you\'ll be known')
    email = EmailField('Email', [
        InputRequired(message='Email address is required'),
        Email(message='Enter a valid email address'),
        Length(max=256, message='Email must not be more than 256 characters'),
        ], description='Enter your email address to help recover your account if lost')
    bio = TextAreaField('Bio', [
        Optional(),
        Length(max=400, message='Bio cannot exceed 400 characters')
        ], description='Tell us about yourself')

# form for uploading profile picture
class UploadPictureForm(FlaskForm):
    picture = FileField('Profile Picture', [
        FileRequired(message='No photo supplied.'),
        FileAllowed(['jpg', 'jpeg', 'png'], message='Profile picture must be a jpg or png file.'),
        ], render_kw={'accept': 'image/jpeg,image/png'}, description='Upload a picture for your account profile')

# form for deleting profile picture
class DeletePictureForm(FlaskForm):
    confirm = SubmitField('Delete Picture')

# form for updating password
class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', [
        InputRequired(message='Please enter your password'),
        PasswordCheck(message='Incorrect password'),
        ], description='Enter your current password')
    new_password = PasswordField('New Password', [
        InputRequired(message='Please choose a new password'),
        Length(min=8, max=256, message='Your new password must be between 8 and 256 characters.'),
        NotEqualTo('current_password', message='New password must be different.')
        ], description='Choose a strong password to protect your account')
    confirm_password = PasswordField('Confirm Password', [
        InputRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
        ], description='Confirm your password')

# form for deleting account
class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', [
        InputRequired(message='Please enter your password'),
        PasswordCheck(message='Incorrect password'),
        ], description='Enter your password to delete your account')

# form for creating and updating recipe
class RecipeForm(FlaskForm):
    title = StringField('Title', [
        InputRequired(message='Title is required'),
        Length(max=100, message='Title cannot be more than 100 characters'),
        ], description='What do you call your recipe?')
    description = TextAreaField('Description', [
        Optional(),
        Length(max=400, message='Desciprtion cannot exceed 400 characters'),
        ], description='Tell us more about your recipe...')
    time = IntegerField('Time', [
        Optional(),
        NumberRange(min=0, message='Time must be positive'),
        ], description='How long does it take to make?')
    servings = IntegerField('Serves', [
        Optional(),
        NumberRange(min=0, message='Servings must be positive'),
        ], description='How many people does this serve?')
    difficulty = IntegerField('Difficulty', [
        Optional(),
        NumberRange(min=1, max=3, message='Difficulty must be between 1 and 3'),
        ], description='How difficult is your recipe?')
    vegetarian = BooleanField('Vegetarian', description='Is your recipe suitable for vegetarians?')
    ingredients = TextAreaField('Ingredients', [
        InputRequired(message='Ingredents are required'),
        Length(max=1000, message='Ingredients cannot exceed 1000 characters'),
        ], description='Enter the ingredients for your recipe, each on a new line')
    method = TextAreaField('Method', [
        InputRequired(message='Method is required'),
        Length(max=4000, message='Method cannot exceed 4000 characters'),
        ], description='Enter the method for your recipe, leaving a blank line between each instruction')
    tags = StringField('Tags', [
        Optional(),
        Length(max=100, message='Tags must not exceed 100 characters'),
        ], description='Enter some keywords to categorise your recipe')

    def filter_tags(form, field):
        if field:
            pretaglist = [x.strip() for x in field.split(',')]
            taglist = []
            d = {}
            for tag in pretaglist:
                if tag.lower() not in d:
                    d[tag.lower()] = True
                    taglist.append(tag)
            return ','.join(taglist)
        else:
            return ''

# form for uploading recipe photo
class PhotoForm(FlaskForm):
    photo = FileField('Photo', [
        FileRequired(message='No photo supplied.'),
        FileAllowed(['jpg', 'jpeg', 'png'], message='Photo must be a jpg or png file.'),
        ], render_kw={'accept': 'image/jpeg,image/png'}, description='Upload a photo of your recipe')

class RateForm(FlaskForm):
    rating = RadioField('Rating', [
        InputRequired(message='Please provide a rating'),
        ], choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], description='Rate this recipe out of 5')

class PostForm(FlaskForm):
    title = StringField('Title', [
        InputRequired(message='Title is required'),
        Length(max=100, message='Title cannot be more than 100 characters'),
        ], description='Give your post a name')
    body = TextAreaField('Body', [
        InputRequired(message='Body is required'),
        Length(max=4000, message='Body cannot be more than 4000 characters'),
        ], description='Write your message here')
    #photos = MultipleFileField('Photos', [
    #    ], render_kw={'accept': 'image/jpeg,image/png'}, description='Upload photos to share')
    sharing = SelectField('Visibility', choices=[('0', 'Only You'), ('1', 'Followers'), ('2', 'Everyone')], description='Who can see your post')

class MultiPhotoForm(FlaskForm):
    photos = MultipleFileField('Photos', render_kw={'accept': 'image/jpeg,image/png'}, description='Upload photos to share')

# form for deleting recipe photo and recipe (for csrf)
class DeleteForm(FlaskForm):
    pass
