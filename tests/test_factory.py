import os

from flask import current_app
from sharecipe import create_app

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_setup(app):
    with app.app_context():
        assert os.path.exists(current_app.instance_path)
        assert os.path.exists(current_app.config['UPLOAD_FOLDER'])

def test_upload(client, app):
    with app.app_context():
        f = open(os.path.join(current_app.config['UPLOAD_FOLDER'], 'hello.txt'), 'w')
        f.write('Hello, World!')
        f.close()

    response = client.get('/uploads/hello.txt')
    assert response.data == b'Hello, World!'
