from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import BooleanField, Field, IntegerField, IntegerRangeField, PasswordField, StringField, TextAreaField
from wtforms.validators import EqualTo, InputRequired, Length, NumberRange, Optional
from wtforms.widgets import TextInput


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired(message='Please enter a username')], description='Enter your username')
    password = PasswordField('Password', [InputRequired(message='Please enter a password')], description='Enter your password')

class RegisterForm(FlaskForm):
    username = StringField('Username', [InputRequired(message='Please choose a username'),Length(min=3, max=36, message='Your username must be between 3 and 36 characters')], description='Choose a unique username to identify your account')
    forename = StringField('Forename', [Optional(), Length(max=36, message='Your forename cannot be more than 36 characters')], description='Enter your forename')
    surname = StringField('Surname', [Optional(), Length(max=36, message='Your surname cannot be more than 36 characters')], description='Enter your surname')
    password = PasswordField('Password', [InputRequired(message='Please choose a password'), Length(min=8, max=256, message='Your password must be between 8 and 256 characters.')], description='Choose a strong password to protect your account')
    confirm_password = PasswordField('Confirm Password', [InputRequired(message='Please confirm your password'), EqualTo('password', message='Passwords must match')], description='Confirm your password')

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

class PhotoForm(FlaskForm):
    photo = FileField('Photo', [
        FileRequired(message='No photo supplied.'),
        FileAllowed(['jpg', 'jpeg', 'png'], message='Photo must be a jpg or png file.'),
        ], render_kw={'accept': 'image/jpeg,image/png'}, description='Upload a photo of your recipe')

class DeleteForm(FlaskForm):
    pass
