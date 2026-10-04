import sys
import os
from sqlalchemy import text

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db

app = create_app()

def alter_schema():
    with app.app_context():
        db.create_all()
        # Using raw SQL to avoid constraints/migration issues
        conn = db.engine.connect()
        
        # 1. Add fields to purchase_orders
        try:
            conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN created_by_id INTEGER REFERENCES users(id)"))
            conn.commit()
            print("Added created_by_id to purchase_orders")
        except Exception as e:
            print("created_by_id already exists or error:", e)
            conn.rollback()

        try:
            conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN approval_reason VARCHAR(255)"))
            conn.commit()
            print("Added approval_reason to purchase_orders")
        except Exception as e:
            print("approval_reason already exists or error:", e)
            conn.rollback()
            
        try:
            conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN delivery_attempts INTEGER DEFAULT 0"))
            conn.commit()
            print("Added delivery_attempts to purchase_orders")
        except Exception as e:
            print("delivery_attempts already exists or error:", e)
            conn.rollback()

        # 2. Add fields to purchase_order_items
        try:
            conn.execute(text("ALTER TABLE purchase_order_items ADD COLUMN forecast_qty INTEGER"))
            conn.execute(text("ALTER TABLE purchase_order_items ADD COLUMN safety_stock INTEGER"))
            conn.execute(text("ALTER TABLE purchase_order_items ADD COLUMN on_hand INTEGER"))
            conn.commit()
            print("Added snapshot fields to purchase_order_items")
        except Exception as e:
            print("snapshot fields already exist or error:", e)
            conn.rollback()

        # 3. Add fields to stock_movements for approvals
        try:
            conn.execute(text("ALTER TABLE stock_movements ADD COLUMN status VARCHAR(50) DEFAULT 'approved'"))
            conn.execute(text("ALTER TABLE stock_movements ADD COLUMN approval_reason VARCHAR(255)"))
            conn.commit()
            print("Added status and approval_reason to stock_movements")
        except Exception as e:
            print("status/approval_reason already exists on stock_movements or error:", e)
            conn.rollback()
            
        # 4. Add max_order_quantity to product_locations
        try:
            conn.execute(text("ALTER TABLE product_locations ADD COLUMN max_order_quantity INTEGER DEFAULT 0"))
            conn.commit()
            print("Added max_order_quantity to product_locations")
        except Exception as e:
            print("max_order_quantity already exists or error:", e)
            conn.rollback()
            
        # 5. Add contact_email to suppliers
        try:
            conn.execute(text("ALTER TABLE suppliers ADD COLUMN contact_email VARCHAR(120)"))
            conn.commit()
            print("Added contact_email to suppliers")
        except Exception as e:
            print("contact_email already exists or error:", e)
            conn.rollback()

        conn.close()

if __name__ == '__main__':
    alter_schema()
