import time
import json
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Notification
from app.schemas import notification_schema, notifications_schema
from app.extensions import db
from app.utils.auth import requires_permission, Permission
from app.utils.errors import api_error

notifications_bp = Blueprint('notifications', __name__)

# stream_notifications route removed to improve dev server performance.
# The frontend now relies solely on standard polling.

@notifications_bp.route('', methods=['GET'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def get_notifications():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    pagination = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).paginate(page=page, per_page=limit, error_out=False)
    return jsonify({
        'items': notifications_schema.dump(pagination.items),
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })

@notifications_bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def mark_notification_read(id):
    user_id = int(get_jwt_identity())
    notification = Notification.query.filter_by(id=id, user_id=user_id).first()
    
    if not notification:
        return api_error("Notification not found", 404)
        
    data = request.get_json()
    if data and 'is_read' in data:
        notification.is_read = data['is_read']
        db.session.commit()
        
    return jsonify(notification_schema.dump(notification))
