from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.auth import requires_permission, Permission, ROLE_PERMISSIONS
from app.models import SystemSetting, AuditLog, User
from app.extensions import db
from datetime import datetime, timedelta, timezone

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/settings', methods=['GET', 'PUT'])
@jwt_required()
@requires_permission(Permission.SYSTEM_SETTINGS_EDIT)
def manage_settings():
    if request.method == 'GET':
        settings = SystemSetting.query.all()
        # Do not send actual secret values to UI, just a mask or boolean
        res = {}
        for s in settings:
            if 'secret' in s.key.lower() or 'password' in s.key.lower() or 'key' in s.key.lower():
                res[s.key] = '********'
            else:
                res[s.key] = s.value
        return jsonify(res), 200
        
    data = request.get_json()
    reason = data.pop('reason', 'System settings updated')
    
    for k, v in data.items():
        if v == '********': continue # skip unedited secrets
        setting = SystemSetting.query.get(k)
        if not setting:
            setting = SystemSetting(key=k, value=str(v))
            db.session.add(setting)
        else:
            setting.value = str(v)
            
    db.session.commit()
    
    # Audit log
    log = AuditLog(
        user_id=get_jwt_identity(),
        action='update_system_settings',
        target_resource='system_settings',
        details=reason
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@requires_permission(Permission.AUDIT_LOG_VIEW)
def get_audit_logs():
    query = AuditLog.query
    
    user_id = request.args.get('user_id')
    if user_id:
        query = query.filter_by(user_id=user_id)
        
    action = request.args.get('action')
    if action:
        query = query.filter_by(action=action)
        
    days = request.args.get('days', type=int)
    if days:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(AuditLog.created_at >= start_date)
        
    # No edit/delete endpoints exist!
    logs = query.order_by(AuditLog.created_at.desc()).limit(100).all()
    
    return jsonify([{
        'id': l.id,
        'user_id': l.user_id,
        'action': l.action,
        'target_resource': l.target_resource,
        'target_id': l.target_id,
        'details': l.details,
        'ip_address': l.ip_address,
        'created_at': l.created_at.isoformat()
    } for l in logs]), 200

@admin_bp.route('/jobs', methods=['GET'])
@jwt_required()
@requires_permission(Permission.JOBS_MANAGE)
def get_jobs():
    # Use raw SQL since we created the table in raw SQL
    conn = db.engine.connect()
    res = conn.execute(db.text("SELECT id, name, status, last_run_at, error_message, created_at FROM background_jobs ORDER BY id DESC LIMIT 50"))
    jobs = []
    for row in res:
        jobs.append({
            'id': row[0],
            'name': row[1],
            'status': row[2],
            'last_run_at': row[3].isoformat() if row[3] else None,
            'error_message': row[4],
            'created_at': row[5].isoformat() if row[5] else None
        })
    conn.close()
    return jsonify(jobs), 200

@admin_bp.route('/jobs/<int:id>/retry', methods=['POST'])
@jwt_required()
@requires_permission(Permission.JOBS_MANAGE)
def retry_job(id):
    conn = db.engine.connect()
    conn.execute(db.text("UPDATE background_jobs SET status = 'pending', error_message = NULL WHERE id = :id"), {'id': id})
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@admin_bp.route('/security', methods=['GET'])
@jwt_required()
@requires_permission(Permission.SECURITY_MANAGE)
def get_security_stats():
    # users without 2FA
    no_2fa = User.query.filter_by(two_factor_enabled=False).all()
    
    # locked accounts
    locked = User.query.filter(User.locked_until > datetime.now(timezone.utc)).all()
    
    # recent failed logins (we just check failed_login_attempts > 0 for now)
    failed = User.query.filter(User.failed_login_attempts > 0).all()
    
    def serialize(u):
        return {'id': u.id, 'name': u.name, 'email': u.email}
        
    return jsonify({
        'no_2fa': [serialize(u) for u in no_2fa],
        'locked': [{'id': u.id, 'name': u.name, 'email': u.email, 'locked_until': u.locked_until.isoformat()} for u in locked],
        'recent_failed': [{'id': u.id, 'name': u.name, 'email': u.email, 'attempts': u.failed_login_attempts} for u in failed]
    }), 200

@admin_bp.route('/security/unlock/<int:user_id>', methods=['POST'])
@jwt_required()
@requires_permission(Permission.SECURITY_MANAGE)
def unlock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.locked_until = None
    user.failed_login_attempts = 0
    db.session.commit()
    
    log = AuditLog(
        user_id=get_jwt_identity(),
        action='unlock_user',
        target_resource='users',
        target_id=user.id,
        details=f"Unlocked user #{user.id}"
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route('/roles-permissions', methods=['GET'])
@jwt_required()
@requires_permission(Permission.USERS_MANAGE) # Admins only
def get_roles_permissions():
    matrix = {}
    for role, perms in ROLE_PERMISSIONS.items():
        matrix[role] = [p.name for p in perms]
    return jsonify(matrix), 200

@admin_bp.route('/locations', methods=['GET', 'POST'])
@jwt_required()
@requires_permission(Permission.SYSTEM_SETTINGS_EDIT)
def manage_locations():
    from app.models import Location
    if request.method == 'GET':
        locations = Location.query.all()
        return jsonify([{'id': l.id, 'name': l.name, 'address': l.address, 'type': l.type} for l in locations])
        
    data = request.get_json()
    loc = Location(
        name=data['name'],
        address=data.get('address'),
        type=data.get('type', 'store')
    )
    db.session.add(loc)
    db.session.commit()
    
    log = AuditLog(
        user_id=get_jwt_identity(),
        action='create_location',
        target_resource='locations',
        target_id=loc.id,
        details=f"Created location {loc.name}"
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'status': 'success', 'id': loc.id}), 201
