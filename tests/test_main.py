def test_index(client, auth):
    response = client.get('/')
    assert b'Login' in response.data
    assert b'Register' in response.data
    assert b'Welcome to Sharecipe!' in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'Settings' in response.data
    assert b'Profile' in response.data
    assert b'Welcome Test' in response.data

def test_about(client):
    assert client.get('/about').status_code == 200


