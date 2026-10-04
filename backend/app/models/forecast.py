from datetime import datetime, timezone
from app.extensions import db

class ForecastResult(db.Model):
    """
    Stores demand forecast results for each product/model combination.
    Enables historical performance tracking and model comparison.
    """
    __tablename__ = 'forecast_results'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    model_name = db.Column(db.String(50), nullable=False)  # ARIMA | Prophet | LSTM | XGBoost | Hybrid Ensemble
    horizon_days = db.Column(db.Integer, nullable=False, default=30)
    predictions = db.Column(db.Text, nullable=False)  # JSON string of prediction array
    confidence_lower = db.Column(db.Text)  # JSON string
    confidence_upper = db.Column(db.Text)  # JSON string
    rmse = db.Column(db.Float)
    mae = db.Column(db.Float)
    mape = db.Column(db.Float)
    r2_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product = db.relationship('Product', backref=db.backref('forecasts', lazy=True))
