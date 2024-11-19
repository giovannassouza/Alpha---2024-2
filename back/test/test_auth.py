def test_google_login(client):
    response = client.get('/login/google')
    assert 