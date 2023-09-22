import pytest

import io
import os

from flask import current_app
from werkzeug.datastructures import ImmutableMultiDict

from sharecipe.db import get_db
from sharecipe.util import check_password_hash

def test_index(client, auth):
    auth.login()
    response = client.get('/account/')
    assert response.headers['Location'] == '/account/profile'

def test_profile(client, app, auth):
    auth.login()
    response = client.get('/account/profile')
    assert b'Test' in response.data
    assert b'This is the test account.' in response.data

    response = client.post('/account/profile', data={'name': 'New Name', 'bio': 'New bio.'})
    with app.app_context():
        assert get_db().execute(
                'SELECT EXISTS(SELECT 1 FROM user WHERE user_id = 1 AND name = "New Name" AND bio = "New bio.")'
                ).fetchone()[0] == 1

    response = client.get('/account/profile')
    assert b'Profile updated successfully.' in response.data

def test_upload_picture(client, app, auth):
    auth.login()
    response = client.get('/account/picture/upload')
    assert response.headers['Location'] == '/account/'
    
    image = open(os.path.join(os.path.dirname(__file__), 'test.jpg'), 'rb')
    response = client.post('/account/picture/upload', data={'picture': (image, 'test.jpg')})
    with app.app_context():
        res = get_db().execute(
                'SELECT picture FROM user WHERE user_id = 1'
                ).fetchone()
        assert res[0] is not None
        assert res[0] in os.listdir(current_app.config['UPLOAD_FOLDER'])

    response = client.get('/account/profile')
    assert b'Profile picture updated successfully.' in response.data

    client.post('/account/picture/upload', data={'picture': (io.BytesIO(b'hello'), 'test.jpg')})
    response = client.get('/account/profile')
    assert b'Unsupported image format.' in response.data

@pytest.mark.parametrize(('file', 'message'), (
    (None, b'No photo supplied.'),
    ((io.BytesIO(b'hello'), 'test.pdf'), b'Profile picture must be a jpg or png file.'),
    ))
def test_upload_picture_validation(client, auth, file, message):
    auth.login()
    client.post('/account/picture/upload', data={'picture': file})
    response = client.get('/account/profile')
    assert message in response.data

def test_delete_picture(client, app, auth):
    auth.login()
    image = open(os.path.join(os.path.dirname(__file__), 'test.jpg'), 'rb')
    client.post('/account/picture/upload', data={'picture': (image, 'test.jpg')})
    
    with app.app_context():
        db = get_db()
        picture = db.execute('SELECT picture FROM user WHERE user_id = 1').fetchone()[0]
        
        client.post('/account/picture/delete')
        assert os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], picture)) == False
        assert db.execute(
                'SELECT picture FROM user WHERE user_id = 1'
                ).fetchone()[0] is None

    response = client.get('/account/profile')
    assert b'Profile picture deleted successfully.' in response.data

    image = open(os.path.join(os.path.dirname(__file__), 'test.jpg'), 'rb')
    client.post('/account/picture/upload', data={'picture': (image, 'test.jpg')})
    with app.app_context():
        db = get_db()
        picture = db.execute('SELECT picture FROM user WHERE user_id = 1').fetchone()[0]
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], picture))
    
    client.post('/account/picture/delete')
    response = client.get('/account/profile')
    assert b'Profile picture deleted successfully' in response.data
    
    client.post('/account/picture/delete')

def test_password(client, app, auth):
    auth.login()
    response = client.get('/account/password')
    assert response.status_code == 200

    response = client.post('/account/password', data={'current_password': 'test', 'new_password': 'password', 'confirm_password': 'password'})
    with app.app_context():
        assert check_password_hash(get_db().execute(
                'SELECT password FROM user WHERE user_id = 1'
                ).fetchone()[0], 'password')

    response = client.get('/account/password')
    assert b'Password updated successfully.' in response.data

@pytest.mark.parametrize(('data', 'messages'), (
    ({'current_password': 'incorrect_password', 'new_password': 'password', 'confirm_password': 'password'}, (b'Incorrect password')),
    ({'current_password': 'password', 'new_password': 'password', 'confirm_password': 'password'}, (b'New password must be different')),
    ))
def test_password_validation(client, auth, data, messages):
    auth.login()
    client.post('/account/password', data={'current_password': 'test', 'new_password': 'password', 'confirm_password': 'password'})
    response = client.post('/account/password', data=data)
    
    for message in messages:
        assert message in response.data

def test_delete(client, app, auth):
    auth.login()
    response = client.get('/account/delete')
    assert response.status_code == 200

    response = client.post('/account/delete', data={'password': 'test'})
    with app.app_context():
        assert get_db().execute(
                'SELECT EXISTS(SELECT 1 FROM user WHERE user_id = 1)'
                ).fetchone()[0] == 0

    response = client.get('/')
    assert b'Account deleted successfully.' in response.data
