from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import PurchaseOrder, PurchaseOrderItem
from app.extensions import db
from app.utils.auth import requires_permission, Permission
from app.utils.errors import api_error
from app.services.po_delivery import send_po_email

po_bp = Blueprint('purchase_orders', __name__)

@po_bp.route('', methods=['GET'])
@jwt_required()
@requires_permission(Permission.ORDERS_VIEW)
def get_pos():
    pos = PurchaseOrder.query.all()
    res = []
    for po in pos:
        res.append({
            'id': po.id,
            'supplier_name': po.supplier.name if po.supplier else 'Unknown',
            'status': po.status,
            'total_amount': po.total_amount,
            'created_at': po.created_at
        })
    return jsonify(res)

@po_bp.route('/<int:id>/approve', methods=['POST'])
@jwt_required()
@requires_permission(Permission.ORDERS_APPROVE)
def approve_po(id):
    po = PurchaseOrder.query.get(id)
    if not po:
        return api_error("PO not found", 404)
        
    if po.status != 'draft':
        return api_error("Only draft POs can be approved", 400)
        
    po.status = 'approved'
    db.session.commit()
    
    # Audit log
    from app.models import AuditLog
    from flask_jwt_extended import current_user
    audit = AuditLog(
        user_id=current_user.id,
        action='approve_po',
        target_resource='purchase_orders',
        details=f"Approved PO #{po.id} for {po.supplier.name}"
    )
    db.session.add(audit)
    db.session.commit()
    
    # In a real system, send this to a background queue
    send_po_email(po.id)
    
    return jsonify({'message': 'PO approved and sent successfully', 'status': po.status})

@po_bp.route('/<int:id>/receive', methods=['POST'])
@jwt_required()
@requires_permission(Permission.MOVEMENT_RECORD)
def receive_po(id):
    po = PurchaseOrder.query.get(id)
    if not po:
        return api_error("PO not found", 404)
        
    if po.status not in ['sent', 'partial']:
        return api_error("PO must be in sent or partial state to receive items", 400)
        
    data = request.json.get('items', [])
    all_fulfilled = True
    
    for item_data in data:
        item_id = item_data.get('id')
        qty = item_data.get('received_qty', 0)
        
        po_item = PurchaseOrderItem.query.get(item_id)
        if po_item and po_item.po_id == po.id:
            po_item.received_quantity += qty
            po_item.product.quantity += qty
            
            if po_item.received_quantity < po_item.quantity:
                all_fulfilled = False
                
    if all_fulfilled:
        po.status = 'fulfilled'
    else:
        po.status = 'partial'
        
    db.session.commit()
    
    from app.models import AuditLog
    from flask_jwt_extended import current_user
    audit = AuditLog(
        user_id=current_user.id,
        action='receive_po',
        target_resource='purchase_orders',
        details=f"Received items for PO #{po.id} (Status: {po.status})"
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({'message': 'Inventory updated successfully', 'status': po.status})
