import pytest
from app.models import User, Location, Product, StaffTask, ProductLocation, StockMovement, CycleCount, Issue, Category
from app.extensions import db
from app import create_app
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-secret-key"
    CORS_ORIGIN = "*"
    DIRECT_URL = None

@pytest.fixture(scope="module")
def app():
    app = create_app(config_class=TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Seed test data
        loc = Location(name="Test Loc")
        db.session.add(loc)
        db.session.commit()
        
        admin = User(name="Admin", email="admin@test.com", password_hash="pass", role="admin", location_id=loc.id)
        staff = User(name="Staff", email="staff@test.com", password_hash="pass", role="staff", location_id=loc.id)
        cat = Category(name="Test Cat")
        db.session.add_all([admin, staff, cat])
        db.session.commit()
        
        product = Product(name="Prod1", sku="P1", category_id=cat.id, unit_price=10)
        db.session.add(product)
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

@pytest.fixture(scope="module")
def staff_headers(app):
    with app.app_context():
        staff = User.query.filter_by(role='staff').first()
        token = create_access_token(identity=str(staff.id))
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture(scope="module")
def admin_headers(app):
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        token = create_access_token(identity=str(admin.id))
        return {'Authorization': f'Bearer {token}'}

def test_get_my_tasks(client, staff_headers):
    # This should return a list of tasks
    response = client.get('/api/v1/staff/tasks', headers=staff_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_update_task_status_unauthorized(client, staff_headers, app):
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        task = StaffTask(user_id=admin.id, type='receiving', status='todo')
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    
    response = client.put(f'/api/v1/staff/tasks/{task_id}/status', headers=staff_headers, json={'status': 'done'})
    assert response.status_code == 403
    
def test_update_task_status_authorized(client, staff_headers, app):
    with app.app_context():
        staff = User.query.filter_by(role='staff').first()
        task = StaffTask(user_id=staff.id, type='picking', status='todo')
        db.session.add(task)
        db.session.commit()
        task_id = task.id
        
    response = client.put(f'/api/v1/staff/tasks/{task_id}/status', headers=staff_headers, json={'status': 'in_progress'})
    assert response.status_code == 200
    assert response.json['new_status'] == 'in_progress'

def test_record_stock_movement_negative(client, staff_headers, app):
    with app.app_context():
        product = Product.query.first()
        staff = User.query.filter_by(role='staff').first()
        loc_id = staff.location_id
        pl = ProductLocation.query.filter_by(product_id=product.id, location_id=loc_id).first()
        if pl:
            pl.quantity = 0
            db.session.commit()
            
    response = client.post('/api/v1/staff/stock-movements', headers=staff_headers, json={
        'product_id': product.id,
        'change_qty': 100,
        'reason': 'outbound'
    })
    assert response.status_code == 400
    assert 'Insufficient stock' in response.json['error']

def test_cycle_count_variance(client, staff_headers, app):
    with app.app_context():
        product = Product.query.first()
        
    response = client.post('/api/v1/staff/cycle-counts', headers=staff_headers, json={
        'product_id': product.id,
        'counted_qty': 9999 # high variance
    })
    assert response.status_code == 201
    assert response.json['state'] == 'pending_review'
    
    with app.app_context():
        staff = User.query.filter_by(role='staff').first()
        issue = Issue.query.filter_by(user_id=staff.id, type='cycle_count_variance').first()
        assert issue is not None
