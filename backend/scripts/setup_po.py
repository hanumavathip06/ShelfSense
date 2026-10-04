import os

# Create Supplier Model
supplier_code = """from app.extensions import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    lead_time_days = db.Column(db.Integer, default=7)
    is_trusted = db.Column(db.Boolean, default=False)
    auto_send_orders = db.Column(db.Boolean, default=False)
    moq = db.Column(db.Integer, default=1)
    pack_size = db.Column(db.Integer, default=1)
    
    products = db.relationship('Product', backref='supplier', lazy=True)
"""

with open("d:/Shashi/ShelfSense/backend/app/models/supplier.py", "w") as f:
    f.write(supplier_code)


# Create PO Model
po_code = """from datetime import datetime, timezone
from app.extensions import db

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    status = db.Column(db.String(50), default='draft') # draft, pending_approval, approved, sent, partial, fulfilled, cancelled
    total_amount = db.Column(db.Float, default=0.0)
    idempotency_key = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    sent_at = db.Column(db.DateTime, nullable=True)
    
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True)
    supplier = db.relationship('Supplier', backref='purchase_orders')

class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    received_quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product')
"""
with open("d:/Shashi/ShelfSense/backend/app/models/purchase_order.py", "w") as f:
    f.write(po_code)


# Create System Settings Model
settings_code = """from app.extensions import db

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
"""
with open("d:/Shashi/ShelfSense/backend/app/models/system_settings.py", "w") as f:
    f.write(settings_code)


# Register in __init__.py
init_path = "d:/Shashi/ShelfSense/backend/app/models/__init__.py"
with open(init_path, "r") as f:
    init_content = f.read()

if "PurchaseOrder" not in init_content:
    imports = "from .supplier import Supplier\\nfrom .purchase_order import PurchaseOrder, PurchaseOrderItem\\nfrom .system_settings import SystemSetting"
    init_content = init_content.replace("from .import_job import ImportJob", "from .import_job import ImportJob\\n" + imports)
    
    exports = "'ImportJob',\\n    'Supplier',\\n    'PurchaseOrder',\\n    'PurchaseOrderItem',\\n    'SystemSetting'"
    init_content = init_content.replace("'ImportJob'", exports)
    
    with open(init_path, "w") as f:
        f.write(init_content)

print("Database Schema created for Phase 6")
