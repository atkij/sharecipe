from flask import Blueprint
from .minecraft_server import BedrockServer

minecraft_blueprint = Blueprint('minecraft', __name__, url_prefix='/minecraft')

server = BedrockServer()

from . import views
