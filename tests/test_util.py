import pytest
import io
from PIL import Image
from werkzeug.datastructures import FileStorage

from sharecipe.util import resize_image

@pytest.mark.parametrize('path', (
    '/account/',
    '/account/profile',
    '/account/picture/upload',
    '/account/picture/delete',
    '/account/password',
    '/account/delete',
    '/recipe/create',
    '/recipe/1/update',
    '/recipe/1/delete',
    '/recipe/1/photo/upload',
    '/recipe/1/photo/delete',
    '/recipe/1/rate',
    '/user/1/follow',
    '/user/1/unfollow',
    ))
def test_login_required(client, auth, path):
    response = client.get(path)
    assert response.headers['Location'] == '/auth/login'

    auth.login()
    response = client.get(path)
    assert response.headers.get('Location', '') != '/auth/login'

def test_resize_image(client, auth, app):
    image = Image.new('RGB', (512, 512))
    b = io.BytesIO()
    image.save(b, 'JPEG')
    new_image = resize_image(b, 1024)
    assert new_image.size == (512, 512)

    image = Image.new('RGB', (2048, 4096))
    b = io.BytesIO()
    image.save(b, 'JPEG')
    new_image = resize_image(b, 1024)
    assert new_image.size == (512, 1024)
    
    image = Image.new('RGB', (4096, 2048))
    b = io.BytesIO()
    image.save(b, 'JPEG')
    new_image = resize_image(b, 1024)
    assert new_image.size == (1024, 512)

    assert resize_image(io.BytesIO(b'hello'), 1024) is None
