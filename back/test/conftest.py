import pytest

from website import create_app, db

@pytest.fixture()
def app():
    app = create_app()
    
    yield app

@pytest.fixture()
def client(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app.test_client()