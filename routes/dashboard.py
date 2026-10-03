from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from database.database import db
from database.models import ImageAnalysis
from routes import record_activity

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/', methods=['GET'])
def index():
    """Public home landing page for Blind Assist."""
    return render_template('index.html')


@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_page():
    """Main accessible dashboard for authenticated users with recent Image Analysis history."""
    settings = current_user.settings
    recent_analyses = []
    try:
        recent_analyses = ImageAnalysis.query.filter_by(user_id=current_user.id)\
            .order_by(ImageAnalysis.created_at.desc()).limit(5).all()
    except Exception as e:
        current_app.logger.warning(f"Error fetching dashboard image analyses: {e}")

    return render_template(
        'dashboard.html',
        user=current_user,
        settings=settings,
        recent_analyses=recent_analyses
    )


@dashboard_bp.route('/profile', methods=['GET'])
@login_required
def profile_page():
    """User profile overview and management."""
    return render_template('profile.html', user=current_user)


@dashboard_bp.route('/api/profile', methods=['POST', 'PUT'])
@login_required
def update_profile():
    """Update editable profile fields (name, phone, emergency contact)."""
    data = request.get_json(silent=True) or request.form.to_dict()

    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    emergency_contact = data.get('emergency_contact', '').strip()

    if not name or len(name) < 2:
        return jsonify({'success': False, 'error': 'Name must be at least 2 characters.'}), 400

    try:
        current_user.name = name
        current_user.phone = phone
        current_user.emergency_contact = emergency_contact
        db.session.commit()

        record_activity(current_user.id, 'Profile Update', 'User updated personal profile details.')

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully.',
            'user': current_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to update profile: {str(e)}'}), 500
