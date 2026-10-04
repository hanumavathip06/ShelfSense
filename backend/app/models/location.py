from app.extensions import db

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)

    # Relationships
    users = db.relationship('User', backref='location', lazy=True)
    stock_movements_source = db.relationship('StockMovement', foreign_keys='StockMovement.source_location_id', backref='source_location', lazy=True)
    stock_movements_destination = db.relationship('StockMovement', foreign_keys='StockMovement.destination_location_id', backref='destination_location', lazy=True)
