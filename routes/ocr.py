import os
import uuid
import base64
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from services.ocr_service import OCRService
from database.database import db
from database.models import ImageAnalysis
from routes import record_activity

ocr_bp = Blueprint('ocr', __name__)


@ocr_bp.route('/ocr', methods=['GET'])
@login_required
def ocr_page():
    """Text Reader (OCR) page with camera capture, file upload, and text-to-speech controls."""
    return render_template('ocr.html', user=current_user)


@ocr_bp.route('/api/ocr', methods=['POST'])
@login_required
def api_ocr():
    """
    Endpoint to process images and extract text using OCR engine.
    Persists file to uploads/ and records analysis in ImageAnalysis table.
    """
    image_data = None
    is_multipart = False

    if 'image' in request.files:
        image_data = request.files['image']
        is_multipart = True
    elif request.is_json:
        data = request.get_json(silent=True) or {}
        image_data = data.get('image')
    elif 'image' in request.form:
        image_data = request.form['image']

    if not image_data:
        return jsonify({
            'success': False,
            'error': 'No image provided for text reading.'
        }), 400

    # Ensure uploads directory
    upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'uploads'))
    os.makedirs(upload_dir, exist_ok=True)

    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_token = uuid.uuid4().hex[:8]
    saved_filename = f"ocr_{timestamp_str}_{safe_token}.jpg"
    target_path = os.path.join(upload_dir, saved_filename)

    try:
        if is_multipart and hasattr(image_data, 'save'):
            original_ext = os.path.splitext(image_data.filename or '')[1].lower()
            if original_ext in ('.jpg', '.jpeg', '.png'):
                saved_filename = f"ocr_{timestamp_str}_{safe_token}{original_ext}"
                target_path = os.path.join(upload_dir, saved_filename)
            image_data.seek(0)
            image_data.save(target_path)
            image_data.seek(0)
        elif isinstance(image_data, str):
            b64_str = image_data
            if 'base64,' in b64_str:
                b64_str = b64_str.split('base64,')[1]
            raw_bytes = base64.b64decode(b64_str)
            with open(target_path, 'wb') as f:
                f.write(raw_bytes)
    except Exception as save_err:
        current_app.logger.warning(f"Could not persist OCR image to disk: {save_err}")

    result = OCRService.extract_text(image_data)

    if result.get('success'):
        extracted_text = result.get('text', '').strip()
        extracted_snippet = extracted_text.replace('\n', ' ')
        if len(extracted_snippet) > 80:
            extracted_snippet = extracted_snippet[:77] + '...'

        # Save to ImageAnalysis table
        try:
            analysis_record = ImageAnalysis(
                user_id=current_user.id,
                image_filename=saved_filename,
                analysis_result=f"OCR: {extracted_text}" if extracted_text else "OCR: No text detected."
            )
            db.session.add(analysis_record)
            db.session.commit()
            result['analysis_id'] = analysis_record.id
            result['image_filename'] = saved_filename
            result['image_url'] = f"/uploads/{saved_filename}"
        except Exception as db_err:
            db.session.rollback()
            current_app.logger.error(f"Database error saving OCR ImageAnalysis: {db_err}")

        record_activity(
            current_user.id,
            'OCR',
            f"Extracted text: \"{extracted_snippet}\""
        )
        return jsonify(result), 200
    else:
        return jsonify(result), 400
