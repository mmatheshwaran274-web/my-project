from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from services.voice_service import VoiceService
from routes import record_activity

voice_bp = Blueprint('voice', __name__)


@voice_bp.route('/voice', methods=['GET'])
@login_required
def voice_page():
    """Voice Assistant page with large microphone interface and live recognition."""
    return render_template('voice.html', user=current_user)


@voice_bp.route('/api/voice', methods=['POST'])
@login_required
def api_voice():
    """Endpoint to interpret voice input commands and return structured assistive responses."""
    data = request.get_json(silent=True) or request.form.to_dict()
    command_text = data.get('command', '').strip()
    user_lang = current_user.settings.language if current_user.settings else 'en'
    language = data.get('language', user_lang)

    if not command_text:
        return jsonify({
            'success': False,
            'error': 'No command was received.',
            'speech': 'Please speak a command.' if language != 'ta' else 'தயவுசெய்து ஒரு கட்டளையை கூறுங்கள்.'
        }), 400

    result = VoiceService.process_command(command_text, language=language)

    # Log in activity history
    record_activity(
        current_user.id,
        'Voice Command',
        f"Recognized voice command: '{command_text}' -> {result.get('label', 'Action')}"
    )

    return jsonify(result), 200
