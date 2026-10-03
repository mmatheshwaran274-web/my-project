import pytest
from app import create_app
from database.database import db
from database.models import User


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_user_registration_success(client):
    """Test successful user registration creates user and settings."""
    payload = {
        'name': 'Alice Wonder',
        'email': 'alice@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'phone': '1234567890',
        'emergency_contact': '9876543210'
    }
    response = client.post('/api/register', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['user']['email'] == 'alice@example.com'


def test_user_registration_duplicate_email(client):
    """Test registration fails when email is already registered."""
    payload = {
        'name': 'Alice Wonder',
        'email': 'duplicate@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }
    client.post('/api/register', json=payload)
    # Duplicate attempt
    response = client.post('/api/register', json=payload)
    assert response.status_code == 409
    data = response.get_json()
    assert data['success'] is False
    assert 'already exists' in data['error']


def test_user_registration_password_mismatch(client):
    """Test registration fails when password and confirm_password do not match."""
    payload = {
        'name': 'Bob Tester',
        'email': 'bob@example.com',
        'password': 'password123',
        'confirm_password': 'mismatchPassword'
    }
    response = client.post('/api/register', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


def test_user_login_success_and_logout(client):
    """Test login with valid credentials and subsequent logout."""
    reg_payload = {
        'name': 'Charlie',
        'email': 'charlie@example.com',
        'password': 'secretpassword',
        'confirm_password': 'secretpassword'
    }
    client.post('/api/register', json=reg_payload)

    # Login
    login_res = client.post('/api/login', json={
        'email': 'charlie@example.com',
        'password': 'secretpassword'
    })
    assert login_res.status_code == 200
    data = login_res.get_json()
    assert data['success'] is True

    # Logout
    logout_res = client.post('/api/logout')
    assert logout_res.status_code == 200


def test_user_login_invalid_password(client):
    """Test login fails with incorrect password."""
    reg_payload = {
        'name': 'David',
        'email': 'david@example.com',
        'password': 'correctpassword',
        'confirm_password': 'correctpassword'
    }
    client.post('/api/register', json=reg_payload)

    login_res = client.post('/api/login', json={
        'email': 'david@example.com',
        'password': 'wrongpassword'
    })
    assert login_res.status_code == 401
    data = login_res.get_json()
    assert data['success'] is False


def test_protected_dashboard_redirects_unauthenticated(client):
    """Test unauthenticated access to dashboard redirects to login."""
    res = client.get('/dashboard', follow_redirects=False)
    assert res.status_code == 302
    assert '/login' in res.headers['Location']
