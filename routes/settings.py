from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from database.database import db
from database.models import UserSettings
from routes import record_activity

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings', methods=['GET'])
@login_required
def settings_page():
    """Accessibility Settings interface."""
    settings = current_user.settings
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    return render_template('settings.html', user=current_user, settings=settings)


@settings_bp.route('/api/settings', methods=['GET'])
@login_required
def api_get_settings():
    """Retrieve user accessibility settings."""
    settings = current_user.settings
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()

    return jsonify({
        'success': True,
        'settings': settings.to_dict()
    }), 200


@settings_bp.route('/api/settings', methods=['POST', 'PUT'])
@login_required
def api_update_settings():
    """Update accessibility settings."""
    data = request.get_json(silent=True) or request.form.to_dict()

    settings = current_user.settings
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)

    # Voice Assistance Toggle
    if 'voice_enabled' in data:
        val = data['voice_enabled']
        settings.voice_enabled = str(val).lower() in ('true', '1', 'yes', 'on')

    # Speech Speed: 0.5x, 1x, 1.5x, 2x
    if 'speech_speed' in data:
        try:
            speed = float(data['speech_speed'])
            if 0.4 <= speed <= 2.5:
                settings.speech_speed = speed
        except ValueError:
            pass

    # High Contrast Toggle
    if 'high_contrast' in data:
        val = data['high_contrast']
        settings.high_contrast = str(val).lower() in ('true', '1', 'yes', 'on')

    # Font Size: small, medium, large, x-large
    if 'font_size' in data:
        font_size = str(data['font_size']).lower()
        if font_size in ('small', 'medium', 'large', 'x-large'):
            settings.font_size = font_size

    # Language: en, ta
    if 'language' in data:
        lang = str(data['language']).lower()
        if lang in ('en', 'ta'):
            settings.language = lang

    try:
        db.session.commit()
        record_activity(current_user.id, 'Settings', 'Updated accessibility preferences.')
        return jsonify({
            'success': True,
            'message': 'Accessibility settings saved successfully.',
            'settings': settings.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to save settings: {str(e)}'}), 500
