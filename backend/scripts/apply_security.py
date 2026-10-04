import os

# 1. Update models/__init__.py
models_init_path = "d:/Shashi/ShelfSense/backend/app/models/__init__.py"
with open(models_init_path, "r") as f:
    content = f.read()
if "AuditLog" not in content:
    content = content.replace("from .forecast import ForecastResult", "from .forecast import ForecastResult\nfrom .audit import AuditLog")
    content = content.replace("'ForecastResult'", "'ForecastResult',\n    'AuditLog'")
    with open(models_init_path, "w") as f:
        f.write(content)

# 2. Update auth.py to log audits and use argon2
auth_py_path = "d:/Shashi/ShelfSense/backend/app/routes/auth.py"
with open(auth_py_path, "r") as f:
    auth_content = f.read()

if "argon2" not in auth_content:
    auth_content = auth_content.replace(
        "from werkzeug.security import check_password_hash",
        "from passlib.hash import argon2"
    )
    # The original was probably check_password_hash(user.password_hash, password)
    # passlib is argon2.verify(password, hash)
    auth_content = auth_content.replace(
        "check_password_hash(user.password_hash, password)",
        "argon2.verify(password, user.password_hash)"
    )
    
    # We also need to add AuditLog imports
    auth_content = auth_content.replace(
        "from app.models import User",
        "from app.models import User, AuditLog"
    )
    
    # Insert audit log on login success
    success_str = "access_token = create_access_token"
    audit_insert = """
    # Audit log login
    audit = AuditLog(user_id=user.id, action='login', ip_address=request.remote_addr)
    db.session.add(audit)
    db.session.commit()
    
    access_token = create_access_token"""
    
    auth_content = auth_content.replace(success_str, audit_insert)
    
    with open(auth_py_path, "w") as f:
        f.write(auth_content)
        
print("Updated auth.py and models/__init__.py")
