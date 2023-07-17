from flask import Blueprint

account_blueprint = Blueprint('account', __name__, url_prefix='/account')

from . import views
