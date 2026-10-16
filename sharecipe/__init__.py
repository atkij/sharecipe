import os
from importlib import metadata
from flask import Flask, current_app, render_template, send_from_directory
from werkzeug.exceptions import HTTPException

from .util import return_url_for, inject_login_form
from .views import profile

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'sharecipe.db'),
            UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
            URL='http://localhost:5000',
            VERSION=metadata.version('sharecipe'),
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

    app.add_template_global(return_url_for, name='return_url_for')
    app.context_processor(inject_login_form)
    app.register_error_handler(HTTPException, error)
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    
    return app

def register_blueprints(app):
    from .views import settings, auth, main, recipe, profile
    
    app.register_blueprint(settings.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(recipe.bp)
    app.register_blueprint(profile.bp)

    app.add_url_rule('/', endpoint='index')
    app.add_url_rule('/uploads/<path:filename>', endpoint='upload', view_func=upload)

def initialize_extensions(app):
    from .database import database

    database.init_app(app)

def upload(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

def error(e):
    return render_template('error.html', e=e), e.code

