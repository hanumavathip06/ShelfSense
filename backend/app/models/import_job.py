from datetime import datetime, timezone
from app.extensions import db

class ImportJob(db.Model):
    __tablename__ = 'import_jobs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False) # 'products', 'stock_movements', 'suppliers'
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending') # pending, mapping, validating, dry_run, importing, completed, failed, rolled_back
    progress = db.Column(db.Integer, default=0) # 0-100
    total_rows = db.Column(db.Integer, default=0)
    processed_rows = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    error_report_ref = db.Column(db.String(255), nullable=True) # S3 key or file path
    mapping_config = db.Column(db.JSON, nullable=True) # User's column mapping
    import_mode = db.Column(db.String(50), default='skip') # 'skip' or 'update'
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship('User', backref='import_jobs')
