import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import Product, Supplier

app = create_app()
with app.app_context():
    supplier = Supplier.query.filter_by(name="Acme Corp").first()
    if not supplier:
        supplier = Supplier(
            name="Acme Corp",
            email="orders@acmecorp.example.com",
            lead_time_days=10,
            is_trusted=True,
            auto_send_orders=True,
            moq=10,
            pack_size=5
        )
        db.session.add(supplier)
        db.session.commit()
        
    from app.models import Category
    cat = Category.query.first()
    if not cat:
        cat = Category(name="Electronics")
        db.session.add(cat)
        db.session.commit()
        
    products = Product.query.limit(3).all()
    if not products:
        p1 = Product(name="Widget A", sku="WID-A", category_id=cat.id, quantity=2, unit_price=15.00, supplier_id=supplier.id)
        p2 = Product(name="Widget B", sku="WID-B", category_id=cat.id, quantity=5, unit_price=25.00, supplier_id=supplier.id)
        db.session.add_all([p1, p2])
        db.session.commit()
        products = [p1, p2]
        
    for p in products:
        p.supplier_id = supplier.id
        p.quantity = 2 # Extremely low stock
    
    db.session.commit()
    print("Seeded Supplier and linked products.")
