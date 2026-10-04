from datetime import datetime, timezone
from app.extensions import db

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    change_qty = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(50), nullable=False) # sale | manual_adjustment | restock | transfer
    source_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    destination_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='approved') # pending_approval, approved, rejected
    approval_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
