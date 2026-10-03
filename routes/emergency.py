from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from database.database import db
from database.models import EmergencyEvent
from routes import record_activity

emergency_bp = Blueprint('emergency', __name__)


def send_emergency_sms_notification(contact_number: str, latitude: float, longitude: float):
    """
    Modular integration hook for external SMS or automated calling services (e.g. Twilio, AWS SNS, GSM).
    Currently logs placeholder without dispatching live SMS or telecommunication costs.
    """
    # Example Twilio / SMS integration:
    # client.messages.create(to=contact_number, from_=TWILIO_PHONE, body=f"EMERGENCY: User needs help at {latitude}, {longitude}")
    pass


@emergency_bp.route('/emergency', methods=['GET'])
@login_required
def emergency_page():
    """Emergency Assistance interface with confirmation modals and accessible controls."""
    return render_template('emergency.html', user=current_user)


@emergency_bp.route('/api/emergency', methods=['POST'])
@login_required
def api_emergency():
    """
    Endpoint to trigger and log an emergency event.
    Stores coordinates and produces spoken reassurance and action guidance.
    """
    data = request.get_json(silent=True) or request.form.to_dict()

    latitude = data.get('latitude')
    longitude = data.get('longitude')
    location_text = data.get('location_text', '').strip()
    user_lang = current_user.settings.language if current_user.settings else 'en'
    language = data.get('language', user_lang)

    try:
        lat = float(latitude) if latitude is not None and latitude != '' else None
        lon = float(longitude) if longitude is not None and longitude != '' else None
    except ValueError:
        lat, lon = None, None

    try:
        event = EmergencyEvent(
            user_id=current_user.id,
            latitude=lat,
            longitude=lon,
            location_text=location_text if location_text else "Current GPS Coordinates",
            status='Active'
        )
        db.session.add(event)
        db.session.commit()

        contact = current_user.emergency_contact or "No contact registered"

        # Modular SMS dispatcher hook
        if current_user.emergency_contact:
            send_emergency_sms_notification(current_user.emergency_contact, lat, lon)

        record_activity(
            current_user.id,
            'Emergency Activation',
            f"Emergency activated! Logged coordinates ({lat}, {lon}). Primary contact: {contact}"
        )

        speech_en = (
            f"Emergency assistance has been activated. Your registered contact is {contact}. "
            "Please stay calm and remain in a safe location."
        )
        speech_ta = (
            f"அவசர உதவி செயல்படுத்தப்பட்டது. உங்கள் தொடர்பு எண் {contact}. "
            "அமைதியாக இருங்கள் மற்றும் பாதுகாப்பான இடத்தில் இருங்கள்."
        )

        instructions_en = [
            "Stay calm and remain in your current safe position if possible.",
            f"Your emergency contact ({contact}) has been logged for this incident.",
            "If in immediate physical danger, dial 112 or local emergency rescue immediately.",
            "Keep your device unlocked and nearby for responder calls."
        ]

        instructions_ta = [
            "அமைதியாக இருந்து பாதுகாப்பான இடத்தில் இருங்கள்.",
            f"உங்கள் அவசர தொடர்பு ({contact}) பதிவு செய்யப்பட்டுள்ளது.",
            "உடனடி ஆபத்து ஏற்பட்டால் 112 என்ற எண்ணை அழைக்கவும்.",
            "தொலைபேசியை அருகில் வைத்துக்கொள்ளவும்."
        ]

        return jsonify({
            'success': True,
            'event_id': event.id,
            'status': event.status,
            'emergency_contact': contact,
            'latitude': lat,
            'longitude': lon,
            'speech': speech_ta if language == 'ta' else speech_en,
            'instructions': instructions_ta if language == 'ta' else instructions_en,
            'created_at': event.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to trigger emergency: {str(e)}'}), 500
