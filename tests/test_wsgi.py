from sharecipe import create_app
from sharecipe.wsgi import application

def test_wsgi():
    assert repr(application) == repr(create_app())
