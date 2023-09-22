import pytest
from flask import g, session
from sharecipe.db import get_db

def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
            '/auth/register', data={'username': 'user', 'name': 'user', 'password': 'password', 'confirm_password': 'password'}
            )
    assert response.headers['Location'] == '/'

    with app.app_context():
        assert get_db().execute(
                'SELECT * FROM user WHERE username = "user"'
                ).fetchone() is not None

@pytest.mark.parametrize(('username', 'name', 'password', 'confirm_password', 'messages'), (
    ('', '', '', '', [b'Username is required', b'Password is required', b'Password confirmation is required']),
    ('a', '', 'a', 'b', [b'Username must be between 3 and 36 characters', b'Password must be between 8 and 256 characters', b'Passwords must match']),
    ('a'*37, 'a'*57, 'a'*257, '', [b'Username must be between 3 and 36 characters', b'Password must be between 8 and 256 characters']),
    ('test', '', 'password', 'password', [b'Username already taken'])
    ))
def test_register_validation(client, username, name, password, confirm_password, messages):
    response = client.post(
            '/auth/register',
            data={'username': username, 'name': name, 'password': password, 'confirm_password': confirm_password}
            )
    for message in messages:
        assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'messages'), (
    ('', '', [b'Username is required', b'Password is required']),
    ('a', 'test', [b'Incorrect username or password']),
    ('test', 'a', [b'Incorrect username or password']),
    ))
def test_login_validation(auth, username, password, messages):
    response = auth.login(username, password)
    for message in messages:
        assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
