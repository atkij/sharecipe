from flask import Blueprint

user_blueprint = Blueprint('user', __name__, url_prefix='/user')
print('hello')

from . import views
