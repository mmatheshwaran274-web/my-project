import io
import base64
import pytest
from PIL import Image, ImageDraw
from app import create_app
from database.database import db
from database.models import User, UserSettings


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Seed test user
        user = User(name='Test User', email='testocr@example.com', emergency_contact='1234567890')
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth_client(app):
    client = app.test_client()
    client.post('/api/login', json={'email': 'testocr@example.com', 'password': 'password123'})
    return client


def generate_sample_image_base64():
    """Create a minimal in-memory test image with sample text."""
    img = Image.new('RGB', (200, 100), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 40), "HELLO WORLD", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{b64}"


def test_ocr_missing_image(auth_client):
    """Test OCR endpoint returns 400 when no image is provided."""
    res = auth_client.post('/api/ocr', json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False


def test_ocr_with_base64_image(auth_client):
    """Test OCR endpoint extracts text or provides fallback text for base64 image."""
    image_b64 = generate_sample_image_base64()
    res = auth_client.post('/api/ocr', json={'image': image_b64})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'text' in data
    assert len(data['text']) > 0


def test_ocr_requires_authentication(app):
    """Test unauthenticated request to OCR endpoint is redirected."""
    client = app.test_client()
    res = client.get('/ocr')
    assert res.status_code == 302
