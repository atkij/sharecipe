from flask import Blueprint

recipe_blueprint = Blueprint('recipe', __name__, url_prefix='/recipe')

from . import views
