import sys
import os
import pytest
from ..app import create_app
from app.extensions import db
from tests.test_config import TestConfig

# Ensure the parent directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

