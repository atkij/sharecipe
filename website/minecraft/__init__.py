from flask import Blueprint
from .minecraft_server import BedrockServer

minecraft_blueprint = Blueprint('minecraft', __name__, template_folder='templates')

server = BedrockServer()

from . import views
