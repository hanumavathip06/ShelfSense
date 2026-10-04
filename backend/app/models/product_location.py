from app.extensions import db
from datetime import datetime, timezone

class ProductLocation(db.Model):
    __tablename__ = 'product_locations'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_threshold = db.Column(db.Integer, nullable=False, default=0)
    max_order_quantity = db.Column(db.Integer, nullable=False, default=0)
    
    product = db.relationship('Product', backref='location_stocks')
    location = db.relationship('Location', backref='product_stocks')
    
    __table_args__ = (
        db.UniqueConstraint('product_id', 'location_id', name='uq_product_location'),
    )
