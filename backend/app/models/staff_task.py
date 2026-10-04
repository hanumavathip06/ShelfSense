from datetime import datetime, timezone
from app.extensions import db

class StaffTask(db.Model):
    __tablename__ = 'staff_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # receiving | picking | cycle_count
    status = db.Column(db.String(20), nullable=False, default='todo') # todo | in_progress | done
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
