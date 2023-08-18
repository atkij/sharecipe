import os
from flask import Flask, render_template, send_from_directory, session, url_for, g
from datetime import datetime

from website.db import get_db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'website.db'),
            UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
            )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOAD_FOLDER'])
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile'))
    except OSError:
        pass
    
    # register utilities
    register_utils(app)

    # register blueprints
    register_blueprints(app)
    
    # register index
    register_index(app)

    # initialize extensions
    initialize_extensions(app)

    # configure logging
    #configure_logging(app)

    # register error handlers
    register_error_handlers(app)
    
    return app

def register_blueprints(app):
    from website.account import account_blueprint
    from website.auth import auth_blueprint
    from website.social import social_blueprint
    from website.recipe import recipe_blueprint
    from website.user import user_blueprint
    
    app.register_blueprint(account_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(social_blueprint)
    app.register_blueprint(recipe_blueprint)
    app.register_blueprint(user_blueprint)

def initialize_extensions(app):
    from website import db
    db.init_app(app)

def register_utils(app):
    @app.before_request
    def load_user():
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                    'SELECT user.* FROM user WHERE user.user_id = ?', (user_id,)
                    ).fetchone()

    @app.route('/uploads/<path:filename>')
    def upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.template_filter('strftime')
    def format_time_filter(s, f):
        return datetime.fromisoformat(s).strftime(f)

    @app.template_test('path')
    def path_exists(path):
        return os.path.exists(path)

    @app.template_global('profile_pic_uri')
    def profile_pic_filename(user_id):
        filename = os.path.join('profile', str(user_id) + '.jpg')
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            return url_for('upload', filename=filename)
        else:
            return url_for('static', filename='profile.svg')

    @app.template_global('path')
    def join_path(*filenames):
        return os.path.join(*filenames)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('405.html'), 405

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

def configure_logging(app):
    import logging
    from flask.logging import default_handler
    from logging.handlers import FileHandler

    #app.logger.removeHandler(default_handler)

    file_handler = FileHandler('website.log')
    file_handler.setLevel(logging.INFO)

    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(filename)s: %(lineno)d]')
    file_handler.setFormatter(file_formatter)

    app.logger.addHandler(file_handler)

def register_index(app):
    @app.route('/')
    def index():
        return render_template('index.html')
