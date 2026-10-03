import re
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from database.database import db
from database.models import User, UserSettings
from routes import record_activity

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


@auth_bp.route('/register', methods=['GET'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
@auth_bp.route('/api/logout', methods=['POST', 'GET'])
@login_required
def logout():
    record_activity(current_user.id, 'Authentication', 'User logged out of Blind Assist.')
    logout_user()
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'success': True, 'message': 'Logged out successfully.', 'redirect': url_for('auth.login_page')})
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json(silent=True) or request.form.to_dict()

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    phone = data.get('phone', '').strip()
    emergency_contact = data.get('emergency_contact', '').strip()

    # Validation
    if not name or len(name) < 2:
        return jsonify({'success': False, 'error': 'Full Name is required (minimum 2 characters).'}), 400

    if not email or not re.match(EMAIL_REGEX, email):
        return jsonify({'success': False, 'error': 'A valid email address is required.'}), 400

    if not password or len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters.'}), 400

    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match.'}), 400

    # Duplicate check
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'success': False, 'error': 'An account with this email already exists.'}), 409

    try:
        user = User(
            name=name,
            email=email,
            phone=phone,
            emergency_contact=emergency_contact
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # obtain user.id

        # Create default accessibility settings
        settings = UserSettings(
            user_id=user.id,
            voice_enabled=True,
            speech_speed=1.0,
            high_contrast=False,
            font_size='medium',
            language='en'
        )
        db.session.add(settings)
        db.session.commit()

        # Automatically log the user in after registration
        login_user(user)
        record_activity(user.id, 'Authentication', 'New account registered and logged in.')

        return jsonify({
            'success': True,
            'message': 'Registration successful! Welcome to Blind Assist.',
            'redirect': url_for('dashboard.dashboard_page'),
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to register account: {str(e)}'}), 500


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or request.form.to_dict()

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = bool(data.get('remember', True))

    if not email or not password:
        return jsonify({'success': False, 'error': 'Please provide both email and password.'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid email or password.'}), 401

    login_user(user, remember=remember)
    record_activity(user.id, 'Authentication', 'User successfully logged in.')

    return jsonify({
        'success': True,
        'message': f'Welcome back, {user.name}!',
        'redirect': url_for('dashboard.dashboard_page'),
        'user': user.to_dict()
    }), 200
