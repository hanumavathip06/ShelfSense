from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, current_user
from app.utils.auth import requires_permission, Permission
from app.models import ImportJob, User
from app.extensions import db
import os
import filetype
from werkzeug.utils import secure_filename
import threading

imports_bp = Blueprint('imports', __name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@imports_bp.route('/upload', methods=['POST'])
@jwt_required()
@requires_permission(Permission.IMPORTS_EXECUTE) # Will only allow Admin/Manager (or scoped Staff)
def upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    entity_type = request.form.get('entity_type')
    if not entity_type in ['products', 'stock_movements', 'suppliers']:
        return jsonify({'error': 'Invalid entity type'}), 400

    if file and allowed_file(file.filename):
        # 1. Size limit
        file.seek(0, os.SEEK_END)
        if file.tell() > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large'}), 400
        file.seek(0)
        
        # 2. Magic byte check
        header = file.read(2048)
        file.seek(0)
        kind = filetype.guess(header)
        
        # For CSV, filetype often returns None because it's just text.
        # But we must ensure it's not an executable disguised as CSV.
        if kind is not None and kind.mime not in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']:
            return jsonify({'error': 'Invalid file content type'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{current_user.id}_{filename}")
        file.save(filepath)
        
        # Create Job
        job = ImportJob(
            user_id=current_user.id,
            entity_type=entity_type,
            filename=filepath,
            status='mapping'
        )
        db.session.add(job)
        db.session.commit()
        
        # Start a background thread to pre-process / auto-detect headers (simulated)
        # In real life, use Celery/Inngest
        from .import_worker import process_import_job
        threading.Thread(target=process_import_job, args=(job.id, 'extract_headers', current_app._get_current_object())).start()
        
        return jsonify({'job_id': job.id, 'status': 'mapping'}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@imports_bp.route('/<int:job_id>/commit', methods=['POST'])
@jwt_required()
@requires_permission(Permission.IMPORTS_EXECUTE)
def commit_import(current_user, job_id):
    job = ImportJob.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    mapping = request.json.get('mapping')
    mode = request.json.get('import_mode', 'skip')
    
    job.mapping_config = mapping
    job.import_mode = mode
    job.status = 'importing'
    db.session.commit()
    
    from .import_worker import process_import_job
    threading.Thread(target=process_import_job, args=(job.id, 'commit', current_app._get_current_object())).start()
    
    return jsonify({'status': 'importing'})

@imports_bp.route('/<int:job_id>', methods=['GET'])
@jwt_required()
@requires_permission(Permission.IMPORTS_EXECUTE)
def get_job_status(current_user, job_id):
    job = ImportJob.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({
        'id': job.id,
        'status': job.status,
        'progress': job.progress,
        'total_rows': job.total_rows,
        'processed_rows': job.processed_rows,
        'error_count': job.error_count
    })
