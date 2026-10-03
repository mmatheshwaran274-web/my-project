from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from services.location_service import LocationService
from routes import record_activity

location_bp = Blueprint('location', __name__)


@location_bp.route('/location', methods=['GET'])
@login_required
def location_page():
    """Location Assistance page providing accessible GPS readout and audio feedback."""
    return render_template('location.html', user=current_user)


@location_bp.route('/api/location', methods=['GET'])
@login_required
def api_location():
    """Endpoint to process, format, and log user coordinates."""
    lat_str = request.args.get('lat')
    lon_str = request.args.get('lon')
    acc_str = request.args.get('acc')
    user_lang = current_user.settings.language if current_user.settings else 'en'
    language = request.args.get('lang', user_lang)

    if not lat_str or not lon_str:
        return jsonify({
            'success': False,
            'error': 'Latitude and longitude coordinates are required.',
            'speech': 'Coordinates not provided. Please enable GPS permissions.'
        }), 400

    try:
        lat = float(lat_str)
        lon = float(lon_str)
        acc = float(acc_str) if acc_str else None
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid numerical coordinates provided.'
        }), 400

    info = LocationService.format_location_info(lat, lon, acc, language=language)

    record_activity(
        current_user.id,
        'Location Request',
        f"GPS Coordinates accessed: {info['location_summary']}"
    )

    return jsonify({
        'success': True,
        **info
    }), 200
