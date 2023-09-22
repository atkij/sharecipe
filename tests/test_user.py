from datetime import datetime
from sharecipe.db import get_db

def test_index(client, auth):
    assert client.get('/user/3').status_code == 404

    response = client.get('/user/1')
    assert b'test' in response.data
    assert b'Recipes' in response.data
    assert b'Following (1)' in response.data
    assert b'Followers (0)' in response.data
    assert datetime.now().strftime('%B %Y').encode('utf8') in response.data
    assert b'Active today' in response.data

    auth.login()
    response = client.get('/user/2')
    assert b'/user/2/unfollow' in response.data

    auth.login(username='other', password='other')
    response = client.get('/user/1')
    assert b'/user/1/follow' in response.data

def test_follow(client, auth, app):
    assert client.get('/user/2/follow').headers['Location'] == '/auth/login'

    auth.login(username='other', password='other')
    for _ in range(2):
        client.get('/user/1/follow')
        with app.app_context():
            db = get_db()
            following = db.execute('SELECT COUNT(*) FROM follower WHERE follower_id = 2').fetchone()
            assert following[0] == 1

def test_unfollow(client, auth, app):
    assert client.get('/user/2/unfollow').headers['Location'] == '/auth/login'

    auth.login()
    client.get('/user/2/unfollow')
    with app.app_context():
        db = get_db()
        following = db.execute('SELECT COUNT(*) FROM follower WHERE follower_id = 1').fetchone()
        assert following[0] == 0
