import pytest
from app import create_app
from app.extensions import db
from app.models import User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key"
    })
    
    with app.app_context():
        db.create_all()
        yield app
        try:
            db.drop_all()
        except Exception:
            pass

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

@pytest.fixture(scope="module")
def test_users(app):
    with app.app_context():
        admin = User(name="Admin", email="admin@test.com", password_hash=generate_password_hash("pass"), role="admin")
        manager = User(name="Manager", email="manager@test.com", password_hash=generate_password_hash("pass"), role="manager")
        staff = User(name="Staff", email="staff@test.com", password_hash=generate_password_hash("pass"), role="staff")
        
        db.session.add_all([admin, manager, staff])
        db.session.commit()
        
        return {
            "admin": create_access_token(identity=str(admin.id), additional_claims={"role": admin.role}),
            "manager": create_access_token(identity=str(manager.id), additional_claims={"role": manager.role}),
            "staff": create_access_token(identity=str(staff.id), additional_claims={"role": staff.role})
        }

ROUTES_TO_TEST = [
    # (method, route, allowed_roles)
    ('GET', '/api/v1/analytics/summary', ['admin', 'manager', 'staff']),
    ('GET', '/api/v1/analytics/trends', ['admin', 'manager', 'staff']),
    ('GET', '/api/v1/analytics/top-products', ['admin', 'manager']),
    ('GET', '/api/v1/analytics/category-stock', ['admin', 'manager', 'staff']),
    ('GET', '/api/v1/analytics/abc-xyz', ['admin', 'manager']),
    ('GET', '/api/v1/analytics/anomalies', ['admin', 'manager']),
    
    ('GET', '/api/v1/categories', ['admin', 'manager', 'staff']),
    ('GET', '/api/v1/categories/1', ['admin', 'manager', 'staff']),
    ('POST', '/api/v1/categories', ['admin', 'manager']),
    ('PUT', '/api/v1/categories/1', ['admin', 'manager']),
    ('DELETE', '/api/v1/categories/1', ['admin', 'manager']),
    
    ('GET', '/api/v1/products', ['admin', 'manager', 'staff']),
    ('GET', '/api/v1/products/1', ['admin', 'manager', 'staff']),
    ('POST', '/api/v1/products', ['admin', 'manager']),
    ('PUT', '/api/v1/products/1', ['admin', 'manager']),
    ('DELETE', '/api/v1/products/1', ['admin', 'manager']),
    ('POST', '/api/v1/products/1/movements', ['admin', 'manager', 'staff']),
    ('GET', '/api/v1/products/1/history', ['admin', 'manager', 'staff']),
    
    ('GET', '/api/v1/restock-alerts', ['admin', 'manager', 'staff']),
    ('GET', '/api/v1/notifications', ['admin', 'manager', 'staff']),
    ('PATCH', '/api/v1/notifications/1', ['admin', 'manager', 'staff']),
    
    ('GET', '/api/v1/users', ['admin']),
    ('GET', '/api/v1/users/1', ['admin']),
    ('POST', '/api/v1/users', ['admin']),
    ('PUT', '/api/v1/users/1', ['admin']),
    ('DELETE', '/api/v1/users/1', ['admin']),
    
    ('GET', '/api/v1/forecast/1', ['admin', 'manager', 'staff']),
    ('GET', '/api/v1/forecast/1/compare', ['admin', 'manager']),
    ('POST', '/api/v1/forecast/1/train', ['admin', 'manager']),
    
    ('GET', '/api/v1/smart-reorder', ['admin', 'manager', 'staff']),
    ('GET', '/api/v1/smart-reorder/1', ['admin', 'manager', 'staff']),
    
    ('GET', '/api/v1/purchase-orders', ['admin', 'manager', 'staff']),
    ('POST', '/api/v1/purchase-orders/1/approve', ['admin', 'manager']),
    ('POST', '/api/v1/purchase-orders/1/receive', ['admin', 'manager', 'staff']),
    
    ('POST', '/api/v1/imports/1/commit', ['admin', 'manager']),
    ('GET', '/api/v1/imports/1', ['admin', 'manager']),
]

@pytest.mark.parametrize("method, route, allowed_roles", ROUTES_TO_TEST)
def test_route_permissions(client, test_users, method, route, allowed_roles):
    for role, token in test_users.items():
        headers = {"Authorization": f"Bearer {token}"}
        
        if method == 'GET':
            response = client.get(route, headers=headers)
        elif method == 'POST':
            response = client.post(route, headers=headers, json={})
        elif method == 'PUT':
            response = client.put(route, headers=headers, json={})
        elif method == 'PATCH':
            response = client.patch(route, headers=headers, json={})
        elif method == 'DELETE':
            response = client.delete(route, headers=headers)
            
        if role in allowed_roles:
            assert response.status_code != 403, f"{role} should be allowed to {method} {route} but got 403"
        else:
            assert response.status_code == 403, f"{role} should NOT be allowed to {method} {route} but got {response.status_code}"
