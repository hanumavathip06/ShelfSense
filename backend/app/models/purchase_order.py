from datetime import datetime, timezone
from app.extensions import db

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(50), default='draft') # draft, pending_approval, approved, sent, partial, fulfilled, cancelled
    total_amount = db.Column(db.Float, default=0.0)
    idempotency_key = db.Column(db.String(100), unique=True, nullable=True)
    approval_reason = db.Column(db.String(255), nullable=True)
    delivery_attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    sent_at = db.Column(db.DateTime, nullable=True)
    
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True)
    supplier = db.relationship('Supplier', backref='purchase_orders')
    created_by = db.relationship('User', backref='created_pos', foreign_keys=[created_by_id])

class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    received_quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Float, nullable=False)
    forecast_qty = db.Column(db.Integer, nullable=True)
    safety_stock = db.Column(db.Integer, nullable=True)
    on_hand = db.Column(db.Integer, nullable=True)
    
    product = db.relationship('Product')
