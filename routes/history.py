from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from database.models import ActivityHistory, ImageAnalysis

history_bp = Blueprint('history', __name__)


@history_bp.route('/history', methods=['GET'])
@login_required
def history_page():
    """Renders the Activity and Image Analysis History view."""
    activities = current_user.activities.limit(100).all()
    analyses = []
    try:
        analyses = ImageAnalysis.query.filter_by(user_id=current_user.id)\
            .order_by(ImageAnalysis.created_at.desc()).limit(100).all()
    except Exception:
        pass
    return render_template(
        'history.html',
        user=current_user,
        activities=activities,
        analyses=analyses
    )


@history_bp.route('/api/history', methods=['GET'])
@login_required
def api_history():
    """Returns JSON serialized list of the current user's activity log."""
    activities = current_user.activities.limit(100).all()
    serialized = [a.to_dict() for a in activities]

    return jsonify({
        'success': True,
        'count': len(serialized),
        'activities': serialized
    }), 200


@history_bp.route('/api/image-analysis/history', methods=['GET'])
@history_bp.route('/api/analysis-history', methods=['GET'])
@login_required
def api_image_analysis_history():
    """
    API endpoint to retrieve the user's previous image analysis history.
    Returns JSON serialized list of ImageAnalysis records linked to current_user.id.
    """
    try:
        analyses = ImageAnalysis.query.filter_by(user_id=current_user.id)\
            .order_by(ImageAnalysis.created_at.desc()).limit(100).all()
        serialized = [a.to_dict() for a in analyses]

        return jsonify({
            'success': True,
            'count': len(serialized),
            'analyses': serialized
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve image analysis history: {str(e)}'
        }), 500
