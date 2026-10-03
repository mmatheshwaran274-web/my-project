import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_login import LoginManager
from config import config
from database.database import db, init_db
from database.models import User


def create_app(config_name=None):
    """Application factory for Blind Assist."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Ensure required runtime folders exist
    upload_folder = app.config.get('UPLOAD_FOLDER', os.path.join(app.root_path, 'uploads'))
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    # Initialize Database & automatically create all tables
    init_db(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = 'Please log in to access this assistive feature.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Static uploads serving route
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(upload_folder, filename)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.voice import voice_bp
    from routes.vision import vision_bp
    from routes.ocr import ocr_bp
    from routes.location import location_bp
    from routes.emergency import emergency_bp
    from routes.history import history_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(voice_bp)
    app.register_blueprint(vision_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(settings_bp)

    # Context processor to inject user settings and app branding into all templates
    @app.context_processor
    def inject_global_settings():
        return {
            'app_name': 'Blind Assist',
            'app_tagline': 'Smart Assistance for Independent Living'
        }

    # Error Handlers
    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'success': False, 'error': 'Requested API endpoint was not found.'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def handle_500(e):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'success': False, 'error': 'An internal server error occurred.'}), 500
        return render_template('404.html', error_code=500, error_message="Something went wrong on our end."), 500

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n==================================================")
    print(f" BLIND ASSIST - Accessible Full-Stack Web App")
    print(f" Tagline: Smart Assistance for Independent Living")
    print(f" Running at: http://127.0.0.1:{port}")
    print(f"==================================================\n")
    app.run(host='127.0.0.1', port=port, debug=True)
