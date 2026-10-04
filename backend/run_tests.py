from app import create_app
from app.extensions import db
from app.models import User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

app = create_app()
app.config.update({
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "JWT_SECRET_KEY": "test-secret-key"
})

with app.app_context():
    print("Creating DB...")
    db.create_all()
    print("Adding users...")
    admin = User(name="Admin", email="admin@test.com", password_hash=generate_password_hash("pass"), role="admin")
    manager = User(name="Manager", email="manager@test.com", password_hash=generate_password_hash("pass"), role="manager")
    staff = User(name="Staff", email="staff@test.com", password_hash=generate_password_hash("pass"), role="staff")
    db.session.add_all([admin, manager, staff])
    db.session.commit()
    
    tokens = {
        "admin": create_access_token(identity=str(admin.id), additional_claims={"role": admin.role}),
        "manager": create_access_token(identity=str(manager.id), additional_claims={"role": manager.role}),
        "staff": create_access_token(identity=str(staff.id), additional_claims={"role": staff.role})
    }

client = app.test_client()

print("Testing staff...")
headers = {"Authorization": f"Bearer {tokens['staff']}"}
res = client.get("/api/v1/users", headers=headers)
print("Staff status:", res.status_code, res.get_json())
assert res.status_code == 403

print("Testing manager...")
headers = {"Authorization": f"Bearer {tokens['manager']}"}
res = client.get("/api/v1/users", headers=headers)
print("Manager status:", res.status_code, res.get_json())
assert res.status_code == 403

print("Testing admin...")
headers = {"Authorization": f"Bearer {tokens['admin']}"}
res = client.get("/api/v1/users", headers=headers)
print("Admin status:", res.status_code)
assert res.status_code != 403

print("All tests passed!")
