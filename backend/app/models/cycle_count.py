from datetime import datetime, timezone
from app.extensions import db

class CycleCount(db.Model):
    __tablename__ = 'cycle_counts'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expected_qty = db.Column(db.Integer, nullable=False)
    counted_qty = db.Column(db.Integer, nullable=False)
    variance = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending_review') # pending_review | accepted | rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
