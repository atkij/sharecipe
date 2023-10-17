from flask import Blueprint

social_blueprint = Blueprint('social', __name__, url_prefix='/social')

from . import views
