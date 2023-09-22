import pytest

from flask_wtf import FlaskForm
from wtforms import Form, StringField
from werkzeug.datastructures import ImmutableMultiDict

from sharecipe.forms import NotEqualTo, PasswordCheck, RecipeForm

@pytest.mark.parametrize(('data', 'messages'), (
    ({'field_a': 'a', 'field_b': 'a', 'field_c': 'a'}, ('Invalid field name \'field_d\'.', 'Field must not be equal to field_a.', 'Password incorrect')),
    ))
def test_not_equal_to(app, auth, data, messages):
    with app.app_context():
        class TestForm(Form):
            field_a = StringField('Test field 1', [NotEqualTo('field_d')])
            field_b = StringField('Test field 2', [NotEqualTo('field_a')])
            field_c = StringField('Test field 3', [PasswordCheck()])

        data = ImmutableMultiDict(data)

        auth.login()
        form = TestForm(data)

        form.validate()

        for message in messages:
            assert [message] in form.errors.values()

@pytest.mark.parametrize(('data', 'output'), (
    ({'title': 'Title', 'ingredients': 'Ingredients', 'method': 'Method'}, ''),
    ({'title': 'Title', 'ingredients': 'Ingredients', 'method': 'Method', 'tags': 'tag one, tag two, tag one'}, 'tag one,tag two'),
    ))
def test_tags(app, data, output):
    with app.app_context():
        data = ImmutableMultiDict(data)
        form = RecipeForm(data)
        
        assert form.filter_tags(form.tags.data) == output
