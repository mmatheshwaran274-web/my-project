from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import db


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """
    Users table representing registered users.
    Contains: id, name, email, password, created_at, plus profile extensions.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    emergency_contact = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    settings = db.relationship(
        'UserSettings',
        backref='user',
        uselist=False,
        cascade='all, delete-orphan'
    )
    activities = db.relationship(
        'ActivityHistory',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='ActivityHistory.created_at.desc()'
    )
    emergency_events = db.relationship(
        'EmergencyEvent',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='EmergencyEvent.created_at.desc()'
    )
    image_analyses = db.relationship(
        'ImageAnalysis',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='ImageAnalysis.created_at.desc()'
    )

    def set_password(self, password_text):
        """Hash and set the user's password across password and password_hash columns."""
        hashed = generate_password_hash(password_text)
        self.password = hashed
        self.password_hash = hashed

    def check_password(self, password_text):
        """Verify the password against stored hash."""
        h = self.password or self.password_hash
        return check_password_hash(h, password_text) if h else False

    def to_dict(self):
        """Serialize user object to dictionary (excluding credentials)."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'emergency_contact': self.emergency_contact,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.email}>'


class ImageAnalysis(db.Model):
    """
    ImageAnalysis table:
    Stores image upload records and AI analysis results.
    Binary image data is NOT stored in the database.
    Image files are saved to the uploads directory, and only
    the filename/path and analysis result are stored here.
    """
    __tablename__ = 'image_analysis'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    image_filename = db.Column(db.String(255), nullable=False)
    analysis_result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)

    def to_dict(self):
        """Serialize image analysis record to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_filename': self.image_filename,
            'image_url': f'/uploads/{self.image_filename}',
            'analysis_result': self.analysis_result,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<ImageAnalysis id={self.id} user_id={self.user_id} file={self.image_filename}>'


class UserSettings(db.Model):
    """
    User accessibility and application preferences.
    """
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    voice_enabled = db.Column(db.Boolean, default=True, nullable=False)
    speech_speed = db.Column(db.Float, default=1.0, nullable=False)
    high_contrast = db.Column(db.Boolean, default=False, nullable=False)
    font_size = db.Column(db.String(20), default='medium', nullable=False)
    language = db.Column(db.String(10), default='en', nullable=False)

    def to_dict(self):
        """Serialize user settings to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'voice_enabled': self.voice_enabled,
            'speech_speed': self.speech_speed,
            'high_contrast': self.high_contrast,
            'font_size': self.font_size,
            'language': self.language
        }

    def __repr__(self):
        return f'<UserSettings user_id={self.user_id}>'


class ActivityHistory(db.Model):
    """
    Audit log of actions performed by visually impaired users.
    """
    __tablename__ = 'activity_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)

    def to_dict(self):
        """Serialize activity log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<ActivityHistory user_id={self.user_id} type={self.activity_type}>'


class EmergencyEvent(db.Model):
    """
    Record of emergency activations.
    """
    __tablename__ = 'emergency_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_text = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Active', nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)

    def to_dict(self):
        """Serialize emergency event to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_text': self.location_text,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<EmergencyEvent user_id={self.user_id} status={self.status}>'
