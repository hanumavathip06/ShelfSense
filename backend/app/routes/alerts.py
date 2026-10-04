from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Product
from app.schemas import products_schema
from app.utils.auth import requires_permission, Permission

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/restock-alerts', methods=['GET'])
@jwt_required()
@requires_permission(Permission.ALERTS_VIEW)
def get_restock_alerts():
    products = Product.query.filter(Product.quantity <= Product.reorder_threshold).all()
    return jsonify(products_schema.dump(products))
