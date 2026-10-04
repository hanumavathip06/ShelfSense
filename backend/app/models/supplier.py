from app.extensions import db

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
    contact_email = db.Column(db.String(120), nullable=True)
    
    products = db.relationship('Product', backref='supplier', lazy=True)
