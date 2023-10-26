import os
import importlib.metadata
from flask import Flask, current_app, render_template, send_from_directory, session, url_for, g
from werkzeug.exceptions import HTTPException

from sharecipe.db import get_db
from sharecipe.util import name_filter

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'sharecipe.db'),
            UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
            URL='',
            VERSION=importlib.metadata.version('sharecipe'),
            )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass
    
    
    # register blueprints
    register_blueprints(app)
    
    # initialize extensions
    initialize_extensions(app)

    app.add_template_filter(name_filter, name='name')
    app.register_error_handler(HTTPException, error)
    
    return app

def register_blueprints(app):
    from sharecipe.account import account_blueprint
    from sharecipe.auth import auth_blueprint
    from sharecipe.main import main_blueprint
    from sharecipe.recipe import recipe_blueprint
    from sharecipe.social import social_blueprint
    from sharecipe.user import user_blueprint
    
    app.register_blueprint(account_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(recipe_blueprint)
    app.register_blueprint(social_blueprint)
    app.register_blueprint(user_blueprint)

    app.add_url_rule('/', endpoint='index')
    app.add_url_rule('/uploads/<path:filename>', endpoint='upload', view_func=upload)

def initialize_extensions(app):
    from sharecipe import db
    from sharecipe import admin
    db.init_app(app)
    admin.init_app(app)

def upload(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

def error(e):
    return render_template('error.html', e=e), e.code

