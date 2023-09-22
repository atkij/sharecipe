import pytest

import io
import os

from flask import current_app

from sharecipe.db import get_db

def test_index(client, auth):
    response = client.get('/recipe/')
    assert b'Create Recipe' not in response.data
    assert b'My Recipes' not in response.data
    assert b'Recipe 1' in response.data
    assert b'Recipe 2' in response.data

    auth.login()
    response = client.get('/recipe/')
    assert b'Create Recipe' in response.data
    assert b'My Recipes' in response.data

def test_view(client, auth):
    response = client.get('/recipe/1')
    assert b'Update' not in response.data
    assert b'Rate' not in response.data

    auth.login()
    response = client.get('/recipe/1')
    assert b'Update' in response.data
    assert b'Rate' not in response.data

    response = client.get('/recipe/2')
    assert b'Update' not in response.data
    assert b'Rate' in response.data

    assert client.get('/recipe/3').status_code == 404

def test_rate(client, app, auth):
    auth.login()
    response = client.get('/recipe/2/rate')
    assert response.headers['Location'] == '/recipe/2'

    client.post('/recipe/1/rate', data={'rating': 3})
    response = client.get('/recipe/1')
    assert b'You cannot rate your own recipe' in response.data

    for i in range(2):
        response = client.post('/recipe/2/rate', data={'rating': str(i+1)})
        with app.app_context():
            assert get_db().execute(
                    'SELECT rating FROM rating WHERE recipe_id = 2 AND user_id = 1'
                    ).fetchone()[0] == i + 1

def test_search(client):
    response = client.get('/recipe/search')
    assert b'No recipes available.' in response.data

    response = client.get('/recipe/search?q=' + 'a'*101)
    assert b'Queries are restricted to 100 characters maximum.'

    response = client.get('/recipe/search?q=Recipe+1')
    data = response.data.decode('utf8')
    assert data.index('Recipe 1') < data.index('Recipe 2')
    response = client.get('/recipe/search?q=Recipe+2')
    data = response.data.decode('utf8')
    assert data.index('Recipe 2') < data.index('Recipe 1')

    response = client.get('/recipe/search?q=vegetarian+Recipe')
    assert b'Recipe 1' in response.data
    assert b'Recipe 2' not in response.data

def test_latest(client):
    response = client.get('/recipe/latest')
    assert b'Recipe 1' in response.data
    assert b'Recipe 2' in response.data

    response = client.get('/recipe/latest?vegetarian=vegetarian')
    assert b'Recipe 1' in response.data
    assert b'Recipe 2' not in response.data

    response = client.get('/recipe/latest?user_id=1')
    assert b'Recipe 1' in response.data
    assert b'Recipe 2' not in response.data

def test_create(client, app, auth):
    auth.login()
    response = client.get('/recipe/create')
    assert response.status_code == 200

    response = client.post('/recipe/create', data={'title': 'New Recipe', 'ingredients': 'Ingredients', 'method': 'Method'})
    assert response.headers['Location'] == '/recipe/3'
    with app.app_context():
        assert get_db().execute(
                'SELECT EXISTS(SELECT 1 FROM recipe WHERE recipe_id = 3 AND title = "New Recipe")'
                ).fetchone()[0] == 1

def test_update(client, app, auth):
    auth.login()
    response = client.get('/recipe/1/update')
    assert b'Recipe 1' in response.data

    response = client.get('/recipe/3/update')
    assert response.status_code == 404
    response = client.get('/recipe/2/update')
    assert response.status_code == 403

    response = client.post('/recipe/1/update', data={'title': 'Updated Title', 'ingredients': 'Ingredients', 'method': 'Method'})
    assert response.headers['Location'] == '/recipe/1'
    with app.app_context():
        assert get_db().execute(
                'SELECT EXISTS(SELECT 1 FROM recipe WHERE recipe_id = 1 AND title = "Updated Title")'
                ).fetchone()[0] == 1

def test_delete(client, app, auth):
    auth.login()
    response = client.get('/recipe/1/delete')
    assert response.headers['Location'] == '/recipe/1'
    response = client.get('/recipe/1')
    assert b'Unable to delete recipe' in response.data

    response = client.get('/recipe/3/delete')
    assert response.status_code == 404
    response = client.get('/recipe/2/delete')
    assert response.status_code == 403
    
    image = open(os.path.join(os.path.dirname(__file__), 'test.jpg'), 'rb')
    client.post('/recipe/1/photo/upload', data={'photo': (image, 'test.jpg')})
    with app.app_context():
        db = get_db()
        photo = db.execute('SELECT photo FROM recipe WHERE recipe_id = 1').fetchone()[0]

        response = client.post('/recipe/1/delete')
        assert response.headers['Location'] == '/recipe/'
        assert os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], photo)) == False
        assert db.execute(
                'SELECT EXISTS(SELECT 1 FROM recipe WHERE recipe_id = 1)'
                ).fetchone()[0] == 0
    
    client.post('/recipe/create', data={'title': 'New Recipe', 'ingredients': 'Ingredients', 'method': 'Method'})
    client.post('/recipe/3/delete')
    response = client.get('/recipe/')
    assert b'Recipe deleted successfully.' in response.data

def test_photo_upload(client, app, auth):
    auth.login()
    response = client.get('/recipe/1/photo/upload')
    assert response.headers['Location'] == '/recipe/1'

    response = client.get('/recipe/3/photo/upload')
    assert response.status_code == 404
    response = client.get('/recipe/2/photo/upload')
    assert response.status_code == 403
    
    response = client.post('/recipe/1/photo/upload', data={'photo': (io.BytesIO(b'hello'), 'test.jpg')})
    assert response.headers['Location'] == '/recipe/1'
    response = client.get('/recipe/1')
    assert b'Unsupported image format.' in response.data

    image = open(os.path.join(os.path.dirname(__file__), 'test.jpg'), 'rb')
    client.post('/recipe/1/photo/upload', data={'photo': (image, 'test.jpg')})
    response = client.get('/recipe/1')
    assert b'Photo uploaded successfully' in response.data

    with app.app_context():
        photo = get_db().execute('SELECT photo FROM recipe WHERE recipe_id = 1').fetchone()[0]

        image = open(os.path.join(os.path.dirname(__file__), 'test.jpg'), 'rb')
        client.post('/recipe/1/photo/upload', data={'photo': (image, 'test.jpg')})

        assert os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], photo)) == False

@pytest.mark.parametrize(('file', 'message'), (
    (None, b'No photo supplied.'),
    ((io.BytesIO(b'hello'), 'test.pdf'), b'Photo must be a jpg or png file.'),
    ))
def test_photo_upload_validation(client, auth, file, message):
    auth.login()
    client.post('/recipe/1/photo/upload', data={'photo': file})
    response = client.get('/recipe/1')
    assert message in response.data

def test_photo_delete(client, app, auth):
    auth.login()
    response = client.get('/recipe/1/photo/delete')
    assert response.headers['Location'] == '/recipe/1'

    response = client.get('/recipe/3/photo/delete')
    assert response.status_code == 404
    response = client.get('/recipe/2/photo/delete')
    assert response.status_code == 403

    client.post('/recipe/1/photo/delete')
    response = client.get('/recipe/1')
    assert b'No photo to delete.' in response.data

    image = open(os.path.join(os.path.dirname(__file__), 'test.jpg'), 'rb')
    client.post('/recipe/1/photo/upload', data={'photo': (image, 'test.jpg')})
    with app.app_context():
        photo = get_db().execute('SELECT photo FROM recipe WHERE recipe_id = 1').fetchone()[0]
        client.post('/recipe/1/photo/delete')
        assert os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], photo)) == False
        assert get_db().execute('SELECT photo FROM recipe WHERE recipe_id = 1').fetchone()[0] is None
    response = client.get('/recipe/1')
    assert b'Photo deleted successfully.' in response.data

