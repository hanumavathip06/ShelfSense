from datetime import datetime, timezone
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff') # admin | manager | staff
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    needs_password_reset = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    session_version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)

    # Relationships
    stock_movements = db.relationship('StockMovement', backref='performed_by_user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    tasks = db.relationship('StaffTask', backref='user', lazy=True)
    cycle_counts = db.relationship('CycleCount', backref='user', lazy=True)
    issues = db.relationship('Issue', backref='user', lazy=True)
