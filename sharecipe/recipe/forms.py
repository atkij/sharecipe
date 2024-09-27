from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import BooleanField, IntegerField, RadioField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, NumberRange, Optional

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

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        InputRequired(message='Comment is required'),
        Length(max=400, message='Comment cannot be more than 400 characters'),
        ], description='Submit a new comment')

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

class FavouriteForm(FlaskForm):
    pass

class DeleteForm(FlaskForm):
    pass
