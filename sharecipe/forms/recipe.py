from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import Form, BooleanField, HiddenField, IntegerField, RadioField, StringField, TextAreaField
from wtforms.fields import FieldList, FormField
from wtforms.widgets import HiddenInput
from wtforms.validators import InputRequired, Length, NumberRange, Optional

class InstructionForm(Form):
    id = IntegerField(
        validators=[Optional()],
        widget=HiddenInput(),
    )
    position =IntegerField(
        validators=[Optional()],
        widget=HiddenInput()
    )
    instruction = TextAreaField('Instruction')

class IngredientForm(Form):
    id = IntegerField(
        validators=[Optional()],
        widget=HiddenInput(),
    )
    position = IntegerField(
        validators=[Optional()],
        widget=HiddenInput()
    )
    ingredient = StringField('Ingredient')

class PartForm(Form):
    id = IntegerField(
        validators=[Optional()],
        widget=HiddenInput()
    )
    position = IntegerField(
        validators=[Optional()],
        widget=HiddenInput()
    )
    name = StringField('Part')
    ingredients = FieldList(FormField(IngredientForm), min_entries=1)

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
    prepare = IntegerField('Prepare', [
        Optional(),
        NumberRange(min=0, message='Prepare must be positive'),
        ], description='How long does it take to prepare?')
    cook = IntegerField('Cook', [
        Optional(),
        NumberRange(min=0, message='Cook must be positive'),
        ], description='How long does it take to cook?')
    serves = StringField('Serves', [
        Optional(),
        Length(max=100, message='Serves cannot be more than 100 characters'),
        ], description='How many people does your recipe serve?')
    vegetarian = BooleanField('Vegetarian', description='Is your recipe suitable for vegetarians?')
    parts = FieldList(FormField(PartForm), min_entries=1)
    method = FieldList(FormField(InstructionForm), min_entries=1)
    # ingredients = TextAreaField('Ingredients', [
    #     InputRequired(message='Ingredents are required'),
    #     Length(max=1000, message='Ingredients cannot exceed 1000 characters'),
    #     ], description='Enter the ingredients for your recipe, each on a new line')
    # method = TextAreaField('Method', [
    #     InputRequired(message='Method is required'),
    #     Length(max=4000, message='Method cannot exceed 4000 characters'),
    #     ], description='Enter the method for your recipe, leaving a blank line between each instruction')
    tags = StringField('Tags', [
        Optional(),
        Length(max=100, message='Tags must not exceed 100 characters'),
        ], description='Enter some keywords to categorise your recipe')

# form for uploading recipe photo
class PhotoForm(FlaskForm):
    photo = FileField('Photo', [
        FileRequired(message='No photo supplied.'),
        FileAllowed(['jpg', 'jpeg', 'png'], message='Photo must be a jpg or png file.'),
        ], render_kw={'accept': 'image/jpeg,image/png'}, description='Upload a photo of your recipe')

class StarForm(FlaskForm):
    pass

class DeleteForm(FlaskForm):
    pass
