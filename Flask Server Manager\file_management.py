from flask import Blueprint, jsonify, request, current_app, send_file
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
import zipfile
import hashlib
from datetime import datetime

file_bp = Blueprint('file', __name__, url_prefix='/api/file')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@file_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Generate file hash
        file_hash = hashlib.md5(file.read()).hexdigest()
        file.seek(0)  # Reset file pointer
        
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'hash': file_hash
        })
        
    return jsonify({'error': 'File type not allowed'}), 400

@file_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    try:
        return send_file(
            os.path.join(current_app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@file_bp.route('/list')
@login_required
def list_files():
    files = []
    for filename in os.listdir(current_app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        files.append({
            'name': filename,
            'size': os.path.getsize(file_path),
            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        })
    return jsonify({'files': files})