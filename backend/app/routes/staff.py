from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from app.utils.auth import requires_permission, Permission
from app.models import StaffTask, CycleCount, Issue, Product, StockMovement, ProductLocation
from app.extensions import db
from datetime import datetime, timezone

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/tasks', methods=['GET'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW) # Or whatever basic permission for staff
def get_my_tasks(current_user):
    tasks = StaffTask.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': t.id,
        'type': t.type,
        'status': t.status,
        'description': t.description,
        'created_at': t.created_at.isoformat()
    } for t in tasks]), 200

@staff_bp.route('/tasks/<int:task_id>/status', methods=['PUT'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def update_task_status(current_user, task_id):
    task = StaffTask.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized: Not your task'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['todo', 'in_progress', 'done']:
        return jsonify({'error': 'Invalid status'}), 400
        
    task.status = new_status
    db.session.commit()
    return jsonify({'status': 'success', 'new_status': task.status}), 200

@staff_bp.route('/stock-movements', methods=['POST'])
@jwt_required()
@requires_permission(Permission.MOVEMENT_RECORD)
def record_stock_movement(current_user):
    data = request.get_json()
    product_id = data.get('product_id')
    change_qty = data.get('change_qty')
    reason = data.get('reason') # inbound, outbound, transfer
    destination_location_id = data.get('destination_location_id')
    
    if not current_user.location_id:
        return jsonify({'error': 'You do not have an assigned location'}), 400
        
    pl = ProductLocation.query.filter_by(product_id=product_id, location_id=current_user.location_id).first()
    if not pl:
        # Create stock location record if it doesn't exist
        pl = ProductLocation(product_id=product_id, location_id=current_user.location_id, quantity=0)
        db.session.add(pl)
    
    if reason == 'outbound' or reason == 'transfer':
        if pl.quantity < abs(change_qty):
            return jsonify({'error': 'Insufficient stock in your location'}), 400
            
        pl.quantity -= abs(change_qty)
        movement = StockMovement(
            product_id=product_id,
            change_qty=-abs(change_qty),
            reason=reason,
            source_location_id=current_user.location_id,
            destination_location_id=destination_location_id if reason == 'transfer' else None,
            performed_by=current_user.id
        )
        db.session.add(movement)
        
        # If transfer, add to destination
        if reason == 'transfer' and destination_location_id:
            dest_pl = ProductLocation.query.filter_by(product_id=product_id, location_id=destination_location_id).first()
            if not dest_pl:
                dest_pl = ProductLocation(product_id=product_id, location_id=destination_location_id, quantity=0)
                db.session.add(dest_pl)
            dest_pl.quantity += abs(change_qty)
            
    elif reason == 'inbound':
        pl.quantity += abs(change_qty)
        movement = StockMovement(
            product_id=product_id,
            change_qty=abs(change_qty),
            reason='inbound',
            destination_location_id=current_user.location_id,
            performed_by=current_user.id
        )
        db.session.add(movement)
    else:
        return jsonify({'error': 'Invalid reason'}), 400
        
    db.session.commit()
    return jsonify({'status': 'success'}), 201

@staff_bp.route('/cycle-counts', methods=['POST'])
@jwt_required()
@requires_permission(Permission.INVENTORY_EDIT)
def create_cycle_count(current_user):
    data = request.get_json()
    product_id = data.get('product_id')
    counted_qty = data.get('counted_qty')
    
    if not current_user.location_id:
        return jsonify({'error': 'You do not have an assigned location'}), 400
        
    pl = ProductLocation.query.filter_by(product_id=product_id, location_id=current_user.location_id).first()
    expected_qty = pl.quantity if pl else 0
    variance = counted_qty - expected_qty
    
    variance_threshold = 5 # Arbitrary threshold, can be configured
    
    status = 'pending_review' if abs(variance) > variance_threshold else 'accepted'
    
    cc = CycleCount(
        product_id=product_id,
        user_id=current_user.id,
        expected_qty=expected_qty,
        counted_qty=counted_qty,
        variance=variance,
        status=status
    )
    db.session.add(cc)
    
    if status == 'pending_review':
        # Create a discrepancy issue for the manager
        issue = Issue(
            user_id=current_user.id,
            product_id=product_id,
            type='cycle_count_variance',
            notes=f'Variance of {variance} detected.',
            status='open'
        )
        db.session.add(issue)
    else:
        # Auto-accept and adjust stock
        if not pl:
            pl = ProductLocation(product_id=product_id, location_id=current_user.location_id, quantity=counted_qty)
            db.session.add(pl)
        else:
            pl.quantity = counted_qty
            
        movement = StockMovement(
            product_id=product_id,
            change_qty=variance,
            reason='cycle_count_adjustment',
            source_location_id=current_user.location_id,
            performed_by=current_user.id
        )
        db.session.add(movement)

    db.session.commit()
    return jsonify({'status': 'success', 'state': status}), 201

@staff_bp.route('/issues', methods=['POST'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def report_issue(current_user):
    data = request.get_json()
    issue = Issue(
        user_id=current_user.id,
        product_id=data.get('product_id'),
        type=data.get('type'),
        notes=data.get('notes'),
        photo_url=data.get('photo_url')
    )
    db.session.add(issue)
    db.session.commit()
    return jsonify({'status': 'success'}), 201

@staff_bp.route('/activity', methods=['GET'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def get_my_activity(current_user):
    movements = StockMovement.query.filter_by(performed_by=current_user.id).order_by(StockMovement.created_at.desc()).limit(10).all()
    counts = CycleCount.query.filter_by(user_id=current_user.id).order_by(CycleCount.created_at.desc()).limit(10).all()
    
    return jsonify({
        'movements': [{
            'id': m.id,
            'product_id': m.product_id,
            'change_qty': m.change_qty,
            'reason': m.reason,
            'created_at': m.created_at.isoformat()
        } for m in movements],
        'cycle_counts': [{
            'id': c.id,
            'product_id': c.product_id,
            'counted_qty': c.counted_qty,
            'variance': c.variance,
            'status': c.status,
            'created_at': c.created_at.isoformat()
        } for c in counts]
    }), 200

@staff_bp.route('/low-stock', methods=['GET'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def get_low_stock(current_user):
    if not current_user.location_id:
        return jsonify({'error': 'You do not have an assigned location'}), 400
        
    low_stock = ProductLocation.query.filter(
        ProductLocation.location_id == current_user.location_id,
        ProductLocation.quantity <= ProductLocation.reorder_threshold
    ).all()
    
    return jsonify([{
        'product_id': p.product_id,
        'quantity': p.quantity,
        'reorder_threshold': p.reorder_threshold
    } for p in low_stock]), 200
