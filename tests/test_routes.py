import io
import base64
import pytest
from PIL import Image
from app import create_app
from database.database import db
from database.models import User, UserSettings, ActivityHistory


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        user = User(
            name='Route Tester',
            email='routes@example.com',
            phone='555-1234',
            emergency_contact='555-9999'
        )
        user.set_password('pass1234')
        db.session.add(user)
        db.session.flush()

        settings = UserSettings(user_id=user.id, speech_speed=1.0, high_contrast=False, font_size='medium', language='en')
        db.session.add(settings)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth_client(app):
    client = app.test_client()
    client.post('/api/login', json={'email': 'routes@example.com', 'password': 'pass1234'})
    return client


def generate_dummy_b64_image():
    img = Image.new('RGB', (100, 100), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"


def test_object_detection_endpoint(auth_client):
    """Test object detection endpoint with valid image payload."""
    img_b64 = generate_dummy_b64_image()
    res = auth_client.post('/api/detect-object', json={'image': img_b64, 'language': 'en'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'objects' in data
    assert 'speech' in data


def test_location_endpoint(auth_client):
    """Test location endpoint returns coordinates and formatted speech."""
    res = auth_client.get('/api/location?lat=13.0827&lon=80.2707&acc=10')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['latitude'] == 13.0827
    assert data['longitude'] == 80.2707
    assert 'openstreetmap.org' in data['map_url']


def test_voice_command_endpoint(auth_client):
    """Test voice endpoint processes commands into actions and routes."""
    res = auth_client.post('/api/voice', json={'command': 'read text', 'language': 'en'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['action'] == 'navigate'
    assert data['url'] == '/ocr'


def test_emergency_activation_endpoint(auth_client):
    """Test triggering an emergency creates an event and returns instructions."""
    res = auth_client.post('/api/emergency', json={'latitude': 13.0827, 'longitude': 80.2707})
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['emergency_contact'] == '555-9999'
    assert len(data['instructions']) > 0


def test_history_endpoint(auth_client):
    """Test retrieving activity history returns recorded actions."""
    res = auth_client.get('/api/history')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'activities' in data


def test_settings_get_and_put(auth_client):
    """Test retrieving and updating accessibility settings."""
    # GET settings
    get_res = auth_client.get('/api/settings')
    assert get_res.status_code == 200
    assert get_res.get_json()['settings']['language'] == 'en'

    # PUT settings
    put_res = auth_client.put('/api/settings', json={
        'high_contrast': True,
        'font_size': 'large',
        'speech_speed': 1.5,
        'language': 'ta'
    })
    assert put_res.status_code == 200
    updated = put_res.get_json()['settings']
    assert updated['high_contrast'] is True
    assert updated['font_size'] == 'large'
    assert updated['language'] == 'ta'


def test_profile_update(auth_client):
    """Test updating user profile fields."""
    res = auth_client.post('/api/profile', json={
        'name': 'Updated Route Tester',
        'phone': '555-0000',
        'emergency_contact': '555-1111'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['user']['name'] == 'Updated Route Tester'
    assert data['user']['emergency_contact'] == '555-1111'
