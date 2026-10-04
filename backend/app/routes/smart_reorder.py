"""
Smart Reorder API Routes for ShelfSense.

Provides endpoints for dynamic reorder point optimization:
- GET /smart-reorder — All products with dynamic reorder recommendations
- GET /smart-reorder/<product_id> — Detailed analysis for a single product
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Product, StockMovement
from app.utils.auth import requires_permission, Permission
from app.utils.errors import api_error
from app.ml.data_preprocessor import get_daily_demand
from app.ml.reorder_optimizer import get_reorder_recommendation

smart_reorder_bp = Blueprint('smart_reorder', __name__)


@smart_reorder_bp.route('', methods=['GET'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def get_all_recommendations():
    """
    Get smart reorder recommendations for all products.
    Returns dynamic reorder points with comparison against static thresholds.
    """
    products = Product.query.all()
    recommendations = []
    
    for product in products:
        movements = StockMovement.query.filter_by(product_id=product.id).all()
        movements_data = [{
            'created_at': m.created_at,
            'change_qty': m.change_qty,
            'reason': m.reason
        } for m in movements]
        
        daily_demand = get_daily_demand(movements_data)
        
        product_data = {
            'quantity': product.quantity,
            'lead_time_days': product.lead_time_days,
            'service_level': product.service_level,
            'unit_price': float(product.unit_price),
            'reorder_threshold': product.reorder_threshold
        }
        
        recommendation = get_reorder_recommendation(product_data, daily_demand['demand'].values)
        recommendation['product_id'] = product.id
        recommendation['product_name'] = product.name
        recommendation['sku'] = product.sku
        
        recommendations.append(recommendation)
    
    # Sort by urgency
    urgency_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    recommendations.sort(key=lambda x: urgency_order.get(x['urgency'], 4))
    
    return jsonify(recommendations)


@smart_reorder_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def get_product_recommendation(product_id):
    """
    Get detailed smart reorder analysis for a single product.
    Includes demand statistics, safety stock calculation, EOQ, and comparison.
    """
    product = Product.query.get(product_id)
    if not product:
        return api_error("Product not found", 404)
    
    movements = StockMovement.query.filter_by(product_id=product.id).all()
    movements_data = [{
        'created_at': m.created_at,
        'change_qty': m.change_qty,
        'reason': m.reason
    } for m in movements]
    
    daily_demand = get_daily_demand(movements_data)
    
    product_data = {
        'quantity': product.quantity,
        'lead_time_days': product.lead_time_days,
        'service_level': product.service_level,
        'unit_price': float(product.unit_price),
        'reorder_threshold': product.reorder_threshold
    }
    
    # Try to use ML forecast for better accuracy
    forecasted_demand = None
    try:
        from app.models import ForecastResult
        import json
        latest_forecast = ForecastResult.query.filter_by(
            product_id=product.id
        ).order_by(ForecastResult.created_at.desc()).first()
        
        if latest_forecast:
            forecasted_demand = json.loads(latest_forecast.predictions)
    except Exception:
        pass
    
    recommendation = get_reorder_recommendation(
        product_data, daily_demand['demand'].values, forecasted_demand
    )
    recommendation['product_id'] = product.id
    recommendation['product_name'] = product.name
    recommendation['sku'] = product.sku
    recommendation['has_forecast_data'] = forecasted_demand is not None
    
    return jsonify(recommendation)
