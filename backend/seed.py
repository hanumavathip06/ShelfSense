"""
Enhanced seed script for ShelfSense with rich stock movement history.
Generates realistic demand patterns for ML model training and evaluation.
"""

import os
import random
from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models import User, Category, Product, StockMovement
from werkzeug.security import generate_password_hash

app = create_app()

def seed_data():
    if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('NODE_ENV') == 'production':
        print("ERROR: Cannot run seed script in production environment.")
        return

    with app.app_context():
        print("Starting seeding process (Development Mode)...")

        # Clear existing data
        db.drop_all()
        db.create_all()

        from app.models import Location
        
        # Seed locations
        loc1 = Location(name="Main Warehouse", address="123 Logistics Blvd")
        loc2 = Location(name="Downtown Store", address="456 High St")
        db.session.add_all([loc1, loc2])
        db.session.commit()
        print("Seeded locations.")

        # Seed users
        admin = User(
            name="Admin User",
            email="admin@shelfsense.com",
            password_hash=generate_password_hash("password123"),
            role="admin",
            location_id=loc1.id
        )
        manager = User(
            name="Manager User",
            email="manager@shelfsense.com",
            password_hash=generate_password_hash("password123"),
            role="manager",
            location_id=loc1.id
        )
        staff = User(
            name="Staff User",
            email="staff@shelfsense.com",
            password_hash=generate_password_hash("password123"),
            role="staff",
            location_id=loc1.id
        )
        db.session.add_all([admin, manager, staff])
        db.session.commit()
        print("Seeded users.")

        # Seed categories
        categories = [
            Category(name="Electronics"),
            Category(name="Office Supplies"),
            Category(name="Furniture"),
            Category(name="Cleaning Supplies"),
            Category(name="Safety Equipment")
        ]
        db.session.add_all(categories)
        db.session.commit()
        print("Seeded categories.")

        # Seed products with lead time and service level
        products = [
            Product(name="Laptop", sku="ELC-001", category_id=categories[0].id,
                    quantity=50, reorder_threshold=10, unit_price=999.99,
                    supplier="TechCorp", lead_time_days=14, service_level=0.95),
            Product(name="Smartphone", sku="ELC-002", category_id=categories[0].id,
                    quantity=150, reorder_threshold=20, unit_price=499.50,
                    supplier="TechCorp", lead_time_days=10, service_level=0.95),
            Product(name="Wireless Mouse", sku="ELC-003", category_id=categories[0].id,
                    quantity=200, reorder_threshold=30, unit_price=29.99,
                    supplier="PeripheralsPro", lead_time_days=5, service_level=0.90),
            Product(name="USB-C Hub", sku="ELC-004", category_id=categories[0].id,
                    quantity=80, reorder_threshold=15, unit_price=45.00,
                    supplier="PeripheralsPro", lead_time_days=7, service_level=0.90),
            Product(name="Notebook", sku="OFF-001", category_id=categories[1].id,
                    quantity=300, reorder_threshold=50, unit_price=2.50,
                    supplier="PaperInc", lead_time_days=3, service_level=0.85),
            Product(name="Pens (Box)", sku="OFF-002", category_id=categories[1].id,
                    quantity=200, reorder_threshold=30, unit_price=15.00,
                    supplier="PenMaker", lead_time_days=3, service_level=0.85),
            Product(name="Printer Paper (Ream)", sku="OFF-003", category_id=categories[1].id,
                    quantity=100, reorder_threshold=20, unit_price=8.99,
                    supplier="PaperInc", lead_time_days=5, service_level=0.90),
            Product(name="Sticky Notes", sku="OFF-004", category_id=categories[1].id,
                    quantity=400, reorder_threshold=80, unit_price=3.50,
                    supplier="PaperInc", lead_time_days=3, service_level=0.80),
            Product(name="Office Chair", sku="FUR-001", category_id=categories[2].id,
                    quantity=20, reorder_threshold=5, unit_price=249.99,
                    supplier="Furnishings LLC", lead_time_days=21, service_level=0.95),
            Product(name="Standing Desk", sku="FUR-002", category_id=categories[2].id,
                    quantity=15, reorder_threshold=3, unit_price=599.99,
                    supplier="Furnishings LLC", lead_time_days=30, service_level=0.95),
            Product(name="Hand Sanitizer", sku="CLN-001", category_id=categories[3].id,
                    quantity=500, reorder_threshold=100, unit_price=4.99,
                    supplier="CleanCo", lead_time_days=5, service_level=0.90),
            Product(name="Disinfectant Spray", sku="CLN-002", category_id=categories[3].id,
                    quantity=300, reorder_threshold=60, unit_price=7.99,
                    supplier="CleanCo", lead_time_days=5, service_level=0.90),
            Product(name="Safety Goggles", sku="SAF-001", category_id=categories[4].id,
                    quantity=100, reorder_threshold=20, unit_price=12.50,
                    supplier="SafetyFirst", lead_time_days=7, service_level=0.95),
            Product(name="Hard Hat", sku="SAF-002", category_id=categories[4].id,
                    quantity=50, reorder_threshold=10, unit_price=25.00,
                    supplier="SafetyFirst", lead_time_days=10, service_level=0.95),
            Product(name="First Aid Kit", sku="SAF-003", category_id=categories[4].id,
                    quantity=30, reorder_threshold=5, unit_price=45.00,
                    supplier="SafetyFirst", lead_time_days=7, service_level=0.97),
        ]
        db.session.add_all(products)
        db.session.commit()
        print("Seeded products.")

        # Generate realistic stock movement history (180 days)
        print("Generating stock movement history (this may take a moment)...")
        
        user_ids = [admin.id, manager.id, staff.id]
        
        # Define demand patterns per product (avg daily sales, variability)
        demand_patterns = {
            'ELC-001': {'avg': 2, 'std': 1.5, 'spike_chance': 0.05},     # Laptop - low volume, occasional spikes
            'ELC-002': {'avg': 5, 'std': 3, 'spike_chance': 0.08},       # Smartphone - moderate, variable
            'ELC-003': {'avg': 8, 'std': 2, 'spike_chance': 0.03},       # Mouse - steady demand
            'ELC-004': {'avg': 3, 'std': 2, 'spike_chance': 0.05},       # USB Hub - low-moderate
            'OFF-001': {'avg': 15, 'std': 4, 'spike_chance': 0.02},      # Notebook - high, stable
            'OFF-002': {'avg': 10, 'std': 3, 'spike_chance': 0.02},      # Pens - moderate, stable
            'OFF-003': {'avg': 6, 'std': 2, 'spike_chance': 0.03},       # Paper - moderate
            'OFF-004': {'avg': 20, 'std': 5, 'spike_chance': 0.02},      # Sticky Notes - high, stable
            'FUR-001': {'avg': 1, 'std': 0.8, 'spike_chance': 0.10},     # Chair - low, spiky
            'FUR-002': {'avg': 0.5, 'std': 0.5, 'spike_chance': 0.15},   # Desk - very low, erratic
            'CLN-001': {'avg': 25, 'std': 8, 'spike_chance': 0.05},      # Sanitizer - high, variable
            'CLN-002': {'avg': 15, 'std': 6, 'spike_chance': 0.05},      # Spray - moderate, variable
            'SAF-001': {'avg': 4, 'std': 2, 'spike_chance': 0.04},       # Goggles - low-moderate
            'SAF-002': {'avg': 2, 'std': 1.5, 'spike_chance': 0.06},     # Hard Hat - low
            'SAF-003': {'avg': 1, 'std': 0.5, 'spike_chance': 0.03},     # First Aid - low, stable
        }
        
        movements = []
        now = datetime.now(timezone.utc)
        
        for product in products:
            pattern = demand_patterns.get(product.sku, {'avg': 5, 'std': 2, 'spike_chance': 0.05})
            running_qty = product.quantity + 500  # Start with higher stock for history
            
            for day_offset in range(180, 0, -1):
                date = now - timedelta(days=day_offset)
                
                # Add weekday effect (lower demand on weekends)
                is_weekend = date.weekday() >= 5
                demand_multiplier = 0.3 if is_weekend else 1.0
                
                # Add monthly seasonality
                month = date.month
                seasonal_multiplier = 1.0
                if month in [11, 12, 1]:  # Winter peak
                    seasonal_multiplier = 1.3
                elif month in [6, 7, 8]:  # Summer dip
                    seasonal_multiplier = 0.8
                
                # Generate daily demand
                base_demand = max(0, int(
                    random.gauss(pattern['avg'], pattern['std'])
                    * demand_multiplier
                    * seasonal_multiplier
                ))
                
                # Occasional demand spike (anomaly)
                if random.random() < pattern['spike_chance']:
                    base_demand = int(base_demand * random.uniform(3, 6))
                
                if base_demand > 0 and running_qty > 0:
                    sale_qty = min(base_demand, running_qty)
                    running_qty -= sale_qty
                    
                    movements.append(StockMovement(
                        product_id=product.id,
                        change_qty=-sale_qty,
                        reason='sale',
                        performed_by=random.choice(user_ids),
                        created_at=date + timedelta(hours=random.randint(8, 18),
                                                    minutes=random.randint(0, 59))
                    ))
                
                # Periodic restock (when stock gets low)
                if running_qty < product.reorder_threshold * 2 and random.random() < 0.3:
                    restock_qty = random.randint(30, 100)
                    running_qty += restock_qty
                    
                    movements.append(StockMovement(
                        product_id=product.id,
                        change_qty=restock_qty,
                        reason='restock',
                        performed_by=admin.id,
                        created_at=date + timedelta(hours=random.randint(6, 10),
                                                    minutes=random.randint(0, 59))
                    ))
                
                # Occasional manual adjustments (inventory corrections)
                if random.random() < 0.02:
                    adj_qty = random.choice([-5, -3, -2, 2, 3, 5])
                    running_qty += adj_qty
                    running_qty = max(0, running_qty)
                    
                    movements.append(StockMovement(
                        product_id=product.id,
                        change_qty=adj_qty,
                        reason='manual_adjustment',
                        performed_by=random.choice([admin.id, manager.id]),
                        created_at=date + timedelta(hours=random.randint(9, 17),
                                                    minutes=random.randint(0, 59))
                    ))
            
            # Update product quantity to match final running total
            product.quantity = max(0, running_qty)
        
        # Bulk insert movements
        db.session.add_all(movements)
        db.session.commit()
        print(f"Seeded {len(movements)} stock movements across {len(products)} products.")
        
        print("Seeding complete!")

if __name__ == '__main__':
    seed_data()
