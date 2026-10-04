import os
import sqlalchemy
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Creating new tables...")
    db.create_all()
    
    print("Adding columns to existing tables...")
    def add_col(table, col, col_def):
        with db.engine.connect() as conn:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_def};"))
                conn.commit()
            except sqlalchemy.exc.ProgrammingError as e:
                if 'already exists' not in str(e) and 'DuplicateColumn' not in str(e.__class__.__name__):
                    print(f"Error {table}.{col}: {e}")
                else:
                    print(f"Column {table}.{col} already exists")
    
    add_col('users', 'location_id', 'INTEGER REFERENCES locations(id)')
    add_col('stock_movements', 'source_location_id', 'INTEGER REFERENCES locations(id)')
    add_col('stock_movements', 'destination_location_id', 'INTEGER REFERENCES locations(id)')

    print("Seeding locations and users...")
    from app.models import Location, User
    
    loc = Location.query.first()
    if not loc:
        loc = Location(name="Main Warehouse", address="123 Main St")
        db.session.add(loc)
        db.session.commit()
    
    users = User.query.all()
    for u in users:
        u.location_id = loc.id
    db.session.commit()
    print("Schema update and location seeding complete!")
